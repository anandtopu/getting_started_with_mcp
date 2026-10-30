// Third example: a real SDK client and server share an in-memory transport.
package main

import (
    "context"
    "testing"
    "github.com/modelcontextprotocol/go-sdk/mcp"
)

func TestNotes(t *testing.T) {
    ctx := context.Background()
    st,ct := mcp.NewInMemoryTransports()
    ss,err := notesServer().Connect(ctx,st,nil); if err!=nil { t.Fatal(err) }; defer ss.Close()
    cs,err := mcp.NewClient(&mcp.Implementation{Name:"contract",Version:"1.0"},nil).Connect(ctx,ct,nil)
    if err!=nil { t.Fatal(err) }; defer cs.Close()
    result,err := cs.CallTool(ctx,&mcp.CallToolParams{Name:"search_notes",Arguments:map[string]any{"query":"release"}})
    if err!=nil || result.IsError { t.Fatalf("search: %v %v",result,err) }
    denied,err := cs.CallTool(ctx,&mcp.CallToolParams{Name:"create_note",Arguments:map[string]any{"title":"x","body":"y","confirmed":false}})
    if err!=nil || !denied.IsError { t.Fatalf("approval: %v %v",denied,err) }
}
