#!/usr/bin/env python3
"""
HTML to Markdown Parser for Free AI Hub
Converts the AI directory HTML into a clean, readable Markdown format.
"""

import re
import json
from html.parser import HTMLParser
from typing import List, Dict, Any


class AIHubParser:
    """Parser for converting Free AI Hub HTML to Markdown"""
    
    def __init__(self, html_content: str):
        self.html_content = html_content
        self.ai_data = []
        self.company_flags = {}
        
    def extract_javascript_data(self) -> None:
        """Extract aiData array and companyFlags from JavaScript"""
        # Extract aiData array
        ai_data_match = re.search(r'const aiData = \[(.*?)\];', self.html_content, re.DOTALL)
        if ai_data_match:
            # Parse the JavaScript array into Python objects
            js_array = ai_data_match.group(1)
            # Clean up and parse each object
            objects = re.findall(r'\{[^}]+\}', js_array, re.DOTALL)
            
            for obj_str in objects:
                ai_item = {}
                # Extract fields
                name_match = re.search(r'name:\s*"([^"]+)"', obj_str)
                category_match = re.search(r'category:\s*"([^"]+)"', obj_str)
                company_match = re.search(r'company:\s*"([^"]+)"', obj_str)
                model_match = re.search(r'model:\s*"([^"]+)"', obj_str)
                desc_match = re.search(r'desc:\s*"([^"]+)"', obj_str)
                tags_match = re.search(r'tags:\s*\[(.*?)\]', obj_str)
                url_match = re.search(r'url:\s*"([^"]+)"', obj_str)
                
                if name_match:
                    ai_item['name'] = name_match.group(1)
                if category_match:
                    ai_item['category'] = category_match.group(1)
                if company_match:
                    ai_item['company'] = company_match.group(1)
                if model_match:
                    ai_item['model'] = model_match.group(1)
                if desc_match:
                    ai_item['desc'] = desc_match.group(1)
                if tags_match:
                    tags_str = tags_match.group(1)
                    tags = re.findall(r'"([^"]+)"', tags_str)
                    ai_item['tags'] = tags
                if url_match:
                    ai_item['url'] = url_match.group(1)
                
                if ai_item:
                    self.ai_data.append(ai_item)
        
        # Extract companyFlags
        flags_match = re.search(r'const companyFlags = \{(.*?)\};', self.html_content, re.DOTALL)
        if flags_match:
            flags_str = flags_match.group(1)
            # Extract each flag mapping
            for line in flags_str.split('\n'):
                match = re.search(r'"([^"]+)":\s*"([^"]+)"', line)
                if match:
                    self.company_flags[match.group(1)] = match.group(2)
    
    def categorize_items(self) -> Dict[str, List[Dict]]:
        """Organize AI items by category"""
        categories = {
            'chatOfficial': {
                'title': '🤖 Chatbots — Official',
                'desc': 'First-party experiences from model makers, with the broadest features and latest updates.',
                'items': []
            },
            'chatMulti': {
                'title': '🤖 Chatbots — Multi-model',
                'desc': 'Mix-and-match multiple models in one place for quick comparisons.',
                'items': []
            },
            'chatLocal': {
                'title': '🤖 Chatbots — Local',
                'desc': 'Run LLMs on your own machine for privacy, speed, and offline access.',
                'items': []
            },
            'ide': {
                'title': '💻 Agentic Coding (IDEs)',
                'desc': 'IDE experiences with built-in agents, autocomplete, and coding workflows.',
                'items': []
            },
            'onlineGen': {
                'title': '🖼️ Text-to-Image AI — Online',
                'desc': 'Fast, browser-based image generators with no install required.',
                'items': []
            },
            'localGen': {
                'title': '🖼️ Text-to-Image AI — Local',
                'desc': 'Installable image tools that run locally for full control and customization.',
                'items': []
            },
            'leaderboard': {
                'title': '🏆 Leaderboards',
                'desc': 'Benchmarks and rankings to compare model performance over time.',
                'items': []
            },
            'other': {
                'title': '🤖 Other',
                'desc': 'Exotic chatbots with smaller models and other AI powered tools.',
                'items': []
            }
        }
        
        for item in self.ai_data:
            category = item.get('category', '')
            
            # Determine the right category
            if category == 'chat':
                model = item.get('model', '').lower()
                if 'multi' in model:
                    categories['chatMulti']['items'].append(item)
                else:
                    categories['chatOfficial']['items'].append(item)
            elif category in ['chatLocal', 'ide', 'onlineGen', 'localGen', 'leaderboard', 'other']:
                categories[category]['items'].append(item)
            else:
                categories['chatOfficial']['items'].append(item)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v['items']}
    
    def format_company_name(self, company: str) -> str:
        """Add country flag to company name if available"""
        flag = self.company_flags.get(company, '')
        return f"{flag} {company}" if flag else company
    
    def item_to_markdown(self, item: Dict) -> str:
        """Convert a single AI item to Markdown format"""
        name = item.get('name', 'Unknown')
        company = self.format_company_name(item.get('company', 'Unknown'))
        model = item.get('model', 'N/A')
        desc = item.get('desc', '')
        tags = item.get('tags', [])
        url = item.get('url', '')
        
        # Format tags as badges
        tags_md = ' '.join([f'`{tag}`' for tag in tags]) if tags else ''
        
        # Build the markdown entry
        md = f"### [{name}]({url})\n\n"
        md += f"**Company:** {company}  \n"
        md += f"**Model:** {model}  \n"
        if tags_md:
            md += f"**Tags:** {tags_md}  \n"
        md += f"\n{desc}\n"
        
        return md
    
    def generate_markdown(self) -> str:
        """Generate the complete Markdown document"""
        self.extract_javascript_data()
        categorized = self.categorize_items()
        
        md = "# Free AI Hub\n\n"
        md += "> A curated list of free AI chatbots and tools.\n\n"
        
        # Table of Contents
        md += "## Table of Contents\n\n"
        for cat_key, cat_data in categorized.items():
            # Create anchor-friendly ID
            anchor = cat_data['title'].lower()
            anchor = re.sub(r'[^\w\s-]', '', anchor)
            anchor = re.sub(r'[\s]+', '-', anchor)
            md += f"- [{cat_data['title']}](#{anchor})\n"
        md += "\n---\n\n"
        
        # Generate each category section
        for cat_key, cat_data in categorized.items():
            md += f"## {cat_data['title']}\n\n"
            md += f"*{cat_data['desc']}*\n\n"
            
            for item in cat_data['items']:
                md += self.item_to_markdown(item)
                md += "\n"
            
            md += "---\n\n"
        
        # Footer
        md += "## About This List\n\n"
        md += "This is a community-maintained list of free AI tools and chatbots. "
        md += "All services listed offer free tiers or are completely free to use.\n\n"
        md += f"**Last Updated:** 2026-02-03  \n"
        md += f"**Total Entries:** {len(self.ai_data)}\n"
        
        return md


def main(html_content=None):
    """Main function to run the parser"""
    # If no content provided, read from stdin
    if html_content is None:
        import sys
        html_content = sys.stdin.read()
    
    # Parse and convert
    parser = AIHubParser(html_content)
    markdown_output = parser.generate_markdown()
    
    # Write to output file
    output_path = 'free_ai_hub.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_output)
    
    print(f"✓ Successfully converted HTML to Markdown")
    print(f"✓ Output saved to: {output_path}")
    print(f"✓ Total entries parsed: {len(parser.ai_data)}")
    
    return markdown_output


if __name__ == "__main__":
    main()
