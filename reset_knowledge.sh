#!/bin/bash

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
