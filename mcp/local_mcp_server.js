#!/usr/bin/env node

/**
 * Local MCP Server for Discovery Coach
 * 
 * This server provides tools for:
 * - Reading/writing files
 * - Mock Jira operations (for testing)
 * - Mock Confluence operations (for testing)
 * 
 * Run: node local_mcp_server.js
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import fs from 'fs/promises';
import path from 'path';

// Initialize MCP server
const server = new Server(
    {
        name: 'discovery-coach-mcp',
        version: '1.0.0',
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

// Tool definitions
const TOOLS = [
    {
        name: 'read_file',
        description: 'Read contents of a file in the Discovery Coach workspace',
        inputSchema: {
            type: 'object',
            properties: {
                path: {
                    type: 'string',
                    description: 'Relative path to the file from workspace root',
                },
            },
            required: ['path'],
        },
    },
    {
        name: 'write_file',
        description: 'Write content to a file in the Discovery Coach workspace',
        inputSchema: {
            type: 'object',
            properties: {
                path: {
                    type: 'string',
                    description: 'Relative path to the file from workspace root',
                },
                content: {
                    type: 'string',
                    description: 'Content to write to the file',
                },
            },
            required: ['path', 'content'],
        },
    },
    {
        name: 'create_jira_epic',
        description: 'Create a new Epic in Jira (mock implementation for testing)',
        inputSchema: {
            type: 'object',
            properties: {
                summary: {
                    type: 'string',
                    description: 'Epic title/summary',
                },
                description: {
                    type: 'string',
                    description: 'Epic description',
                },
                project: {
                    type: 'string',
                    description: 'Jira project key (e.g., PROJ)',
                },
            },
            required: ['summary', 'description', 'project'],
        },
    },
    {
        name: 'search_jira',
        description: 'Search for Jira issues (mock implementation for testing)',
        inputSchema: {
            type: 'object',
            properties: {
                query: {
                    type: 'string',
                    description: 'JQL query or search text',
                },
            },
            required: ['query'],
        },
    },
    {
        name: 'create_confluence_page',
        description: 'Create a Confluence page (mock implementation for testing)',
        inputSchema: {
            type: 'object',
            properties: {
                title: {
                    type: 'string',
                    description: 'Page title',
                },
                content: {
                    type: 'string',
                    description: 'Page content (HTML or markdown)',
                },
                space: {
                    type: 'string',
                    description: 'Confluence space key',
                },
            },
            required: ['title', 'content', 'space'],
        },
    },
];

// Handle list tools request
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: TOOLS,
    };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
        switch (name) {
            case 'read_file': {
                const filePath = path.join(process.cwd(), args.path);
                const content = await fs.readFile(filePath, 'utf-8');
                return {
                    content: [
                        {
                            type: 'text',
                            text: content,
                        },
                    ],
                };
            }

            case 'write_file': {
                const filePath = path.join(process.cwd(), args.path);
                await fs.mkdir(path.dirname(filePath), { recursive: true });
                await fs.writeFile(filePath, args.content, 'utf-8');
                return {
                    content: [
                        {
                            type: 'text',
                            text: `Successfully wrote to ${args.path}`,
                        },
                    ],
                };
            }

            case 'create_jira_epic': {
                // Mock implementation - in production, this would call Jira API
                const epicKey = `${args.project}-${Math.floor(Math.random() * 1000)}`;
                const result = {
                    key: epicKey,
                    id: Math.floor(Math.random() * 100000),
                    summary: args.summary,
                    description: args.description,
                    project: args.project,
                    url: `https://your-jira.atlassian.net/browse/${epicKey}`,
                };

                return {
                    content: [
                        {
                            type: 'text',
                            text: `✅ Created Epic ${epicKey}\n\nSummary: ${args.summary}\nURL: ${result.url}\n\n(Mock implementation - no actual Jira Epic created)`,
                        },
                    ],
                };
            }

            case 'search_jira': {
                // Mock implementation - in production, this would call Jira API
                const mockResults = [
                    {
                        key: 'PROJ-123',
                        summary: 'Implement SSO authentication',
                        status: 'In Progress',
                    },
                    {
                        key: 'PROJ-456',
                        summary: 'User login improvements',
                        status: 'To Do',
                    },
                ].filter((issue) =>
                    issue.summary.toLowerCase().includes(args.query.toLowerCase())
                );

                return {
                    content: [
                        {
                            type: 'text',
                            text: `Found ${mockResults.length} issues matching "${args.query}":\n\n${mockResults
                                .map((issue) => `• ${issue.key}: ${issue.summary} [${issue.status}]`)
                                .join('\n')}\n\n(Mock implementation - showing sample data)`,
                        },
                    ],
                };
            }

            case 'create_confluence_page': {
                // Mock implementation - in production, this would call Confluence API
                const pageId = Math.floor(Math.random() * 1000000);
                const result = {
                    id: pageId,
                    title: args.title,
                    space: args.space,
                    url: `https://your-confluence.atlassian.net/wiki/spaces/${args.space}/pages/${pageId}`,
                };

                return {
                    content: [
                        {
                            type: 'text',
                            text: `✅ Created Confluence page "${args.title}"\n\nSpace: ${args.space}\nURL: ${result.url}\n\n(Mock implementation - no actual Confluence page created)`,
                        },
                    ],
                };
            }

            default:
                throw new Error(`Unknown tool: ${name}`);
        }
    } catch (error) {
        return {
            content: [
                {
                    type: 'text',
                    text: `Error executing ${name}: ${error.message}`,
                },
            ],
            isError: true,
        };
    }
});

// Start the server
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error('Discovery Coach MCP Server running on stdio');
    console.error('Available tools:', TOOLS.map((t) => t.name).join(', '));
}

main().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
});
