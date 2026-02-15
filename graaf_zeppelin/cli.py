#!/usr/bin/env python3
"""
Command-line interface for Graaf Zeppelin knowledge graph conversions.
"""

import argparse
import sys
from pathlib import Path

from .converters import (
    json_to_gexf,
    gexf_to_json,
    json_to_markdown,
    markdown_to_json,
)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Graaf Zeppelin - Knowledge Graph Format Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert JSON to GEXF
  python -m graaf_zeppelin.cli convert knowledge_graph.json graph.gexf
  
  # Convert JSON to Markdown
  python -m graaf_zeppelin.cli convert knowledge_graph.json graph.md
  
  # Convert GEXF to JSON
  python -m graaf_zeppelin.cli convert graph.gexf knowledge_graph.json
  
  # Convert Markdown to JSON
  python -m graaf_zeppelin.cli convert graph.md knowledge_graph.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert between formats')
    convert_parser.add_argument('input', help='Input file path')
    convert_parser.add_argument('output', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'convert':
        input_path = Path(args.input)
        output_path = Path(args.output)
        
        if not input_path.exists():
            print(f"Error: Input file '{input_path}' does not exist")
            sys.exit(1)
        
        input_ext = input_path.suffix.lower()
        output_ext = output_path.suffix.lower()
        
        try:
            # Determine conversion based on file extensions
            if input_ext == '.json' and output_ext == '.gexf':
                print(f"Converting {input_path} (JSON) → {output_path} (GEXF)")
                json_to_gexf(str(input_path), str(output_path))
                
            elif input_ext == '.gexf' and output_ext == '.json':
                print(f"Converting {input_path} (GEXF) → {output_path} (JSON)")
                gexf_to_json(str(input_path), str(output_path))
                
            elif input_ext == '.json' and output_ext == '.md':
                print(f"Converting {input_path} (JSON) → {output_path} (Markdown)")
                json_to_markdown(str(input_path), str(output_path))
                
            elif input_ext == '.md' and output_ext == '.json':
                print(f"Converting {input_path} (Markdown) → {output_path} (JSON)")
                markdown_to_json(str(input_path), str(output_path))
                
            else:
                print(f"Error: Unsupported conversion from {input_ext} to {output_ext}")
                print("Supported conversions:")
                print("  - JSON (.json) ↔ GEXF (.gexf)")
                print("  - JSON (.json) ↔ Markdown (.md)")
                sys.exit(1)
            
            print(f"✓ Successfully converted to {output_path}")
            
        except Exception as e:
            print(f"Error during conversion: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
