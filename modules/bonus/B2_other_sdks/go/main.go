// Lumen notes in the official Go SDK. Run: go run .
// All logs use stderr; MCP owns stdout. Restart clears confirmed writes.
package main

import (
	"context"
	"fmt"
	"github.com/modelcontextprotocol/go-sdk/mcp"
	"log"
	"strings"
	"sync"
)

type Note struct {
	ID    int      `json:"id"`
	Title string   `json:"title"`
	Body  string   `json:"body"`
	Tags  []string `json:"tags"`
}
type Search struct {
	Query string `json:"query"`
}
type Found struct {
	Result []Note `json:"result"`
}
type Create struct {
	Title     string `json:"title"`
	Body      string `json:"body"`
	Confirmed bool   `json:"confirmed"`
}
type Tag struct {
	NoteID    int    `json:"note_id"`
	Tag       string `json:"tag"`
	Confirmed bool   `json:"confirmed"`
}

func notesServer() *mcp.Server {
	server := mcp.NewServer(&mcp.Implementation{Name: "Lumen notes Go", Version: "1.0.0"}, nil)
	notes := []Note{{1, "Release handover", "Review the release checklist.", []string{"release"}}}
	var mu sync.Mutex
	read := &mcp.ToolAnnotations{ReadOnlyHint: true, DestructiveHint: new(bool), IdempotentHint: true, OpenWorldHint: new(bool)}
	write := &mcp.ToolAnnotations{DestructiveHint: new(bool), OpenWorldHint: new(bool)}
	mcp.AddTool(server, &mcp.Tool{Name: "search_notes", Description: "Find synthetic notes by title or body. Empty query lists all.", Annotations: read},
		func(ctx context.Context, req *mcp.CallToolRequest, in Search) (*mcp.CallToolResult, Found, error) {
			mu.Lock()
			defer mu.Unlock()
			out := Found{Result: []Note{}}
			if len(in.Query) > 100 {
				return nil, out, fmt.Errorf("Query exceeds 100 characters")
			}
			for _, n := range notes {
				if strings.Contains(strings.ToLower(n.Title+" "+n.Body), strings.ToLower(in.Query)) {
					out.Result = append(out.Result, n)
				}
			}
			return nil, out, nil
		})
	mcp.AddTool(server, &mcp.Tool{Name: "create_note", Description: "Create an ephemeral note after explicit human confirmation.", Annotations: write},
		func(ctx context.Context, req *mcp.CallToolRequest, in Create) (*mcp.CallToolResult, map[string]any, error) {
			if !in.Confirmed {
				return nil, nil, fmt.Errorf("Confirmation required")
			}
			if len(in.Title) < 1 || len(in.Title) > 100 || len(in.Body) < 1 || len(in.Body) > 2000 {
				return nil, nil, fmt.Errorf("Invalid note size")
			}
			mu.Lock()
			defer mu.Unlock()
			n := Note{len(notes) + 1, in.Title, in.Body, []string{}}
			notes = append(notes, n)
			return nil, map[string]any{"id": n.ID, "title": n.Title}, nil
		})
	mcp.AddTool(server, &mcp.Tool{Name: "tag_note", Description: "Add a tag once after confirmation.", Annotations: write},
		func(ctx context.Context, req *mcp.CallToolRequest, in Tag) (*mcp.CallToolResult, map[string]any, error) {
			if !in.Confirmed {
				return nil, nil, fmt.Errorf("Confirmation required")
			}
			if len(in.Tag) < 1 || len(in.Tag) > 40 {
				return nil, nil, fmt.Errorf("Invalid tag size")
			}
			mu.Lock()
			defer mu.Unlock()
			for i := range notes {
				if notes[i].ID == in.NoteID {
					found := false
					for _, t := range notes[i].Tags {
						if t == in.Tag {
							found = true
						}
					}
					if !found {
						notes[i].Tags = append(notes[i].Tags, in.Tag)
					}
					return nil, map[string]any{"id": in.NoteID, "tags": notes[i].Tags}, nil
				}
			}
			return nil, nil, fmt.Errorf("Note not found")
		})
	registerContext(server)
	return server
}

func main() {
	if err := notesServer().Run(context.Background(), &mcp.StdioTransport{}); err != nil {
		log.Fatal(err)
	}
}
