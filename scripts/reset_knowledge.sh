#!/bin/bash

# Discovery Coach - Reset Knowledge Base Script
# Deletes and rebuilds the RAG vector database

# Get the directory where this script is located and go to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "🔄 Resetting Discovery Coach Knowledge Base"
echo "============================================"
echo ""

# Check if rag_db exists
if [ -d "rag_db" ]; then
    echo "📁 Current RAG database found"
    RAG_SIZE=$(du -sh rag_db 2>/dev/null | cut -f1)
    echo "   Size: $RAG_SIZE"
    echo ""
    
    # Confirm deletion
    read -p "⚠️  This will delete the existing knowledge base. Continue? (y/N) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Operation cancelled"
        exit 1
    fi
    
    echo "🗑️  Deleting old knowledge base..."
    rm -rf rag_db
    echo "✅ Old knowledge base deleted"
else
    echo "📁 No existing RAG database found"
fi

echo ""
echo "🔨 Rebuilding knowledge base..."
echo "   This will process all files in data/knowledge_base/"
echo ""

# Count knowledge base files
KB_COUNT=$(find data/knowledge_base -name "*.txt" 2>/dev/null | wc -l | tr -d ' ')
echo "   Found $KB_COUNT text files to index"
echo ""

# Check if server is running
if lsof -Pi :8050 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Server is currently running"
    echo "   The knowledge base will be rebuilt on next server restart"
    echo ""
    echo "To apply changes now:"
    echo "   1. Run: ./stop.sh"
    echo "   2. Run: ./start.sh"
else
    echo "✅ Server is not running"
    echo "   The knowledge base will be built on next server start"
    echo ""
    echo "To build now, run: ./start.sh"
fi

echo ""
echo "============================================"
echo "✅ Reset complete"


# Discovery Coach - Reset Knowledge Base Script
# Removes the vector database so it will rebuild with new knowledge files

echo "🗑️  Discovery Coach - Reset Knowledge Base"
echo "=========================================="
echo ""

# Check if rag_db exists
if [ -d "rag_db" ]; then
    # Get size before deletion
    RAG_SIZE=$(du -sh rag_db 2>/dev/null | cut -f1)
    echo "📚 Current knowledge base size: $RAG_SIZE"
    echo ""
    echo "⚠️  This will delete the vector database."
    echo "   It will be rebuilt from knowledge_base/*.txt on next startup."
    echo ""
    read -p "Continue? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing rag_db..."
        rm -rf rag_db
        
        if [ ! -d "rag_db" ]; then
            echo "✅ Knowledge base removed successfully"
            echo ""
            echo "Next steps:"
            echo "1. Add new .txt files to knowledge_base/ folder"
            echo "2. Run ./start.sh to rebuild the knowledge base"
        else
            echo "❌ Failed to remove knowledge base"
            exit 1
        fi
    else
        echo "❌ Cancelled"
        exit 0
    fi
else
    echo "ℹ️  No knowledge base found (rag_db doesn't exist)"
    echo ""
    echo "The knowledge base will be created automatically when you:"
    echo "1. Add .txt files to knowledge_base/ folder"
    echo "2. Run ./start.sh"
fi

echo "=========================================="
