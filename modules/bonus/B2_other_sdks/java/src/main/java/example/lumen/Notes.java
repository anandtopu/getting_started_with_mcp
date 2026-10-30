package example.lumen;

// Example 1. Stable Java SDK 2.1 speaks 2025-11-25: this is a labeled compatibility lesson.
import io.modelcontextprotocol.server.*;
import io.modelcontextprotocol.server.transport.StdioServerTransportProvider;
import io.modelcontextprotocol.json.McpJsonDefaults;
import io.modelcontextprotocol.spec.McpSchema.*;
import java.util.*;
import java.util.concurrent.CountDownLatch;

public final class Notes {
    private static final List<Map<String,Object>> notes = new ArrayList<>();
    static { notes.add(new HashMap<>(Map.of("id",1,"title","Release handover","body","Review the release checklist.","tags",new ArrayList<>(List.of("release"))))); }
    static CallToolResult result(Object value, boolean error) {
        try { return CallToolResult.builder().addTextContent(McpJsonDefaults.getMapper().writeValueAsString(value)).isError(error).build(); }
        catch (Exception e) { throw new IllegalStateException("Serialization failed", e); }
    }
    static synchronized CallToolResult call(String name, Map<String,Object> args) {
        if (name.equals("search_notes")) {
            String q = (String)args.getOrDefault("query", "");
            if (q.length()>100) return result("Query exceeds 100 characters",true);
            return result(Map.of("result",notes.stream().filter(n -> (n.get("title")+" "+n.get("body")).toLowerCase(Locale.ROOT).contains(q.toLowerCase(Locale.ROOT))).toList()),false);
        }
        if (!Boolean.TRUE.equals(args.get("confirmed"))) return result("Confirmation required",true);
        if (name.equals("create_note")) {
            String title=(String)args.get("title"), body=(String)args.get("body");
            if (title==null || body==null || title.isEmpty() || title.length()>100 || body.isEmpty() || body.length()>2000) return result("Invalid note size",true);
            int id=notes.size()+1; notes.add(new HashMap<>(Map.of("id",id,"title",title,"body",body,"tags",new ArrayList<String>())));
            return result(Map.of("id",id,"title",title),false);
        }
        String tag=(String)args.get("tag");
        if (tag==null || tag.isEmpty() || tag.length()>40) return result("Invalid tag size",true);
        int id=((Number)args.get("note_id")).intValue();
        for (var n:notes) if (((Number)n.get("id")).intValue()==id) {
            @SuppressWarnings("unchecked") var tags=(List<String>)n.get("tags");
            if (!tags.contains(tag)) tags.add(tag);
            return result(Map.of("id",id,"tags",tags),false);
        }
        return result("Note not found",true);
    }
    public static void main(String[] args) throws Exception {
        var transport=new StdioServerTransportProvider(McpJsonDefaults.getMapper());
        var server=McpServer.sync(transport).serverInfo("Lumen notes Java", "1.0.0")
            .capabilities(ServerCapabilities.builder().tools(false).resources(false,false).prompts(false).build()).build();
        for (String name:List.of("search_notes","create_note","tag_note")) {
            Map<String,Object> properties=new HashMap<>();
            List<String> required=new ArrayList<>();
            if (name.equals("search_notes")) properties.put("query",Map.of("type","string","maxLength",100));
            else {
                properties.put("confirmed",Map.of("type","boolean","default",false));
                if (name.equals("create_note")) { properties.put("title",Map.of("type","string","minLength",1,"maxLength",100)); properties.put("body",Map.of("type","string","minLength",1,"maxLength",2000)); required.addAll(List.of("title","body")); }
                else { properties.put("note_id",Map.of("type","integer")); properties.put("tag",Map.of("type","string","minLength",1,"maxLength",40)); required.addAll(List.of("note_id","tag")); }
            }
            var tool=Tool.builder().name(name).description(name.equals("search_notes")?"Find synthetic notes by title or body.":"Change an ephemeral note only after explicit human confirmation.")
                .inputSchema(Map.of("type","object","properties",properties,"required",required,"additionalProperties",false))
                .annotations(new ToolAnnotations(null,name.equals("search_notes"),false,!name.equals("create_note"),false,false)).build();
            server.addTool(new McpServerFeatures.SyncToolSpecification(tool,(exchange,request)->call(name,request.arguments())));
        }
        NoteContext.register(server);
        Runtime.getRuntime().addShutdownHook(new Thread(server::close));
        new CountDownLatch(1).await();
    }
}
