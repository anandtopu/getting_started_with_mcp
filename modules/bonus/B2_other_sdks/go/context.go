// Second example: resources and prompts use the same registered service.
package main

import (
	"context"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

func registerContext(server *mcp.Server) {
	server.AddResource(&mcp.Resource{URI: "lumen://notes/help", Name: "Notes policy", MIMEType: "text/plain"},
		func(ctx context.Context, req *mcp.ReadResourceRequest) (*mcp.ReadResourceResult, error) {
			return &mcp.ReadResourceResult{Contents: []*mcp.ResourceContents{{URI: req.Params.URI, MIMEType: "text/plain", Text: "Review exact note text before creating. Restart clears writes."}}}, nil
		})
	server.AddPrompt(&mcp.Prompt{Name: "review_notes", Description: "Review notes without changing them"},
		func(ctx context.Context, req *mcp.GetPromptRequest) (*mcp.GetPromptResult, error) {
			return &mcp.GetPromptResult{Messages: []*mcp.PromptMessage{{Role: "user", Content: &mcp.TextContent{Text: "Search release notes and cite evidence. Do not write without approval."}}}}, nil
		})
}
