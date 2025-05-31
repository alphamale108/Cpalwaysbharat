import os
import re
import logging
from typing import List, Dict, Optional
from pathlib import Path
from jinja2 import Template
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from .extractors import get_extractor
from utilities.database import MongoDB
from utilities.drm_utils import apply_drm
from utilities.file_utils import process_text_file, clean_temp_files, download_file
from utilities.html_generator import generate_html_portal

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MongoDB
db = MongoDB(os.getenv("MONGODB_URI"))

# Create Pyrogram client
app = Client(
    "drm_uploader_bot",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# HTML template for the portal
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Portal - {{title}}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
            color: white;
            padding: 20px 0;
            text-align: center;
            border-radius: 0 0 10px 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        h1 {
            margin: 0;
            font-size: 2.2em;
        }
        .search-box {
            margin: 20px 0;
            text-align: center;
        }
        #searchInput {
            padding: 10px 15px;
            width: 70%;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        .content-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .content-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .content-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        .card-image {
            height: 180px;
            overflow: hidden;
        }
        .card-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .card-body {
            padding: 15px;
        }
        .card-title {
            font-size: 1.2em;
            margin: 0 0 10px 0;
            color: #333;
        }
        .card-meta {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 15px;
        }
        .quality-selector {
            margin-bottom: 10px;
        }
        select {
            padding: 5px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        .download-btn {
            display: inline-block;
            background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            transition: background 0.3s ease;
        }
        .download-btn:hover {
            background: linear-gradient(135deg, #5d3a99 0%, #8c40ab 100%);
        }
        .no-results {
            text-align: center;
            grid-column: 1 / -1;
            padding: 40px;
            color: #666;
        }
        footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
        @media (max-width: 768px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
            #searchInput {
                width: 90%;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{{title}}</h1>
            <p>Access all your course materials in one place</p>
        </div>
    </header>

    <div class="container">
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search for videos, PDFs..." onkeyup="searchContent()">
        </div>

        <div class="content-grid" id="contentGrid">
            {% for item in content_items %}
            <div class="content-card" data-title="{{item.title|lower}}" data-type="{{item.type}}">
                <div class="card-image">
                    <img src="{{item.thumbnail or 'https://via.placeholder.com/300x180?text=No+Thumbnail'}}" alt="{{item.title}}">
                </div>
                <div class="card-body">
                    <h3 class="card-title">{{item.title}}</h3>
                    <div class="card-meta">
                        <span>{{item.type|upper}}</span> • 
                        <span>{{item.duration|default('N/A')}}</span>
                    </div>
                    
                    {% if item.type == 'video' %}
                    <div class="quality-selector">
                        <select id="quality-{{loop.index}}">
                            {% for quality in item.qualities %}
                            <option value="{{quality.url}}">{{quality.resolution}} ({{quality.size}})</option>
                            {% endfor %}
                        </select>
                    </div>
                    {% endif %}
                    
                    <a href="{{item.download_url}}" class="download-btn" download>
                        Download {{item.type|upper}}
                    </a>
                </div>
            </div>
            {% else %}
            <div class="no-results">
                <p>No content available yet. Please check back later.</p>
            </div>
            {% endfor %}
        </div>
    </div>

    <footer>
        <div class="container">
            <p>Generated by DRM Uploader Bot • {{timestamp}}</p>
        </div>
    </footer>

    <script>
        function searchContent() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const grid = document.getElementById('contentGrid');
            const cards = grid.getElementsByClassName('content-card');

            for (let i = 0; i < cards.length; i++) {
                const title = cards[i].getAttribute('data-title');
                const type = cards[i].getAttribute('data-type');
                
                if (title.includes(filter) || type.includes(filter)) {
                    cards[i].style.display = "";
                } else {
                    cards[i].style.display = "none";
                }
            }
        }
    </script>
</body>
</html>
"""

async def generate_html_portal(title: str, content_items: List[Dict]) -> str:
    """Generate HTML portal from content items"""
    from datetime import datetime
    
    # Prepare template data
    template_data = {
        'title': title,
        'content_items': content_items,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Create HTML from template
    template = Template(HTML_TEMPLATE)
    html_content = template.render(template_data)
    
    # Save to file
    output_file = f"course_portal_{int(datetime.now().timestamp())}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_file

async def process_content(message: Message, content_url: str) -> Optional[Dict]:
    """Process content from URL and return info dict"""
    try:
        msg = await message.reply_text("🔍 Analyzing link...")
        
        # Get appropriate extractor
        extractor = get_extractor(content_url)
        if not extractor:
            await msg.edit_text("❌ Unsupported link/platform")
            return None
        
        # Extract content info
        content_info = await extractor.extract(content_url)
        await msg.edit_text(f"✅ Extracted: {content_info['title']}")
        
        # Download content
        await msg.edit_text("📥 Downloading content...")
        content_info['file_path'] = await download_file(
            content_info['download_url'],
            content_info['type'],
            quality=content_info.get('preferred_quality')
        )
        
        # Apply DRM if video
        if content_info['type'] == 'video':
            await msg.edit_text("🔒 Applying DRM protection...")
            content_info['file_path'] = await apply_drm(content_info)
        
        return content_info
    
    except Exception as e:
        logger.error(f"Error processing content: {str(e)}", exc_info=True)
        await message.reply_text(f"❌ Error processing content: {str(e)}")
        return None
    finally:
        clean_temp_files()

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text(
        "👋 Hello! I'm Advanced Course Portal Bot\n\n"
        "I can create beautiful HTML portals from:\n"
        "- Text files with course links\n"
        "- Appx/ClassPlus/Utkarsh courses\n"
        "- Direct video/PDF links\n\n"
        "Send me a text file or links to get started!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Help Guide", callback_data="help")]
        ])
    )

@app.on_message(filters.command(["help", "guide"]))
async def help_command(client: Client, message: Message):
    help_text = """
📚 **Advanced Course Portal Bot Help** 📚

🔹 **Supported Content:**
- Text files with multiple course links
- Appx courses (no login needed)
- ClassPlus courses (no login needed)
- Utkarsh classes
- Direct video links (MP4, M3U8, etc.)
- Direct PDF links

🔹 **Key Features:**
- Beautiful HTML portal generation
- Quality selection for videos
- Search functionality
- Mobile-responsive design
- Direct download links

🔹 **How to Use:**
1. Send me a text file with course links
2. Or send individual course links
3. I'll generate a portal or direct download
4. Access content through the HTML interface

🔹 **Admin Commands:**
/adduser - Authorize new user
/removeuser - Remove user access
/stats - View bot statistics
"""
    await message.reply_text(help_text)

@app.on_message(filters.command("portal"))
async def create_portal(client: Client, message: Message):
    """Create HTML portal from text file"""
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply_text("❌ Please reply to a text file with /portal")
        return
    
    try:
        msg = await message.reply_text("📥 Downloading text file...")
        file_path = await message.reply_to_message.download()
        
        await msg.edit_text("🔍 Processing file content...")
        links = await process_text_file(file_path)
        
        if not links:
            await msg.edit_text("❌ No valid links found in file")
            return
            
        await msg.edit_text(f"🔄 Found {len(links)} links. Processing content...")
        
        content_items = []
        success_count = 0
        
        for link in links:
            try:
                content_info = await process_content(message, link)
                if content_info:
                    content_items.append({
                        'title': content_info['title'],
                        'type': content_info['type'],
                        'thumbnail': content_info.get('thumbnail'),
                        'duration': content_info.get('duration_formatted', 'N/A'),
                        'download_url': content_info['file_path'],
                        'qualities': content_info.get('qualities', [])
                    })
                    success_count += 1
            except Exception as e:
                logger.error(f"Error processing link {link}: {str(e)}")
                await message.reply_text(f"⚠️ Skipped {link}: {str(e)}")
        
        if not content_items:
            await msg.edit_text("❌ No content could be processed")
            return
        
        await msg.edit_text("🛠 Generating HTML portal...")
        portal_file = await generate_html_portal("My Course Portal", content_items)
        
        await msg.edit_text("📤 Uploading portal...")
        await message.reply_document(
            document=portal_file,
            caption=f"🌐 Your Course Portal ({success_count}/{len(links)} items)"
        )
        
        await msg.delete()
        
    except Exception as e:
        logger.error(f"Portal creation error: {str(e)}", exc_info=True)
        await message.reply_text(f"❌ Error creating portal: {str(e)}")
    finally:
        clean_temp_files()

@app.on_message(filters.text | filters.document)
async def handle_content(client: Client, message: Message):
    """Handle all incoming content (text links and documents)"""
    user_id = message.from_user.id
    if not db.is_user_authorized(user_id):
        await message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    if message.document:
        if message.document.file_name.endswith('.txt'):
            await create_portal(client, message)
        return
    
    text = message.text.strip()
    if re.match(r'https?://\S+', text):
        content_info = await process_content(message, text)
        if content_info:
            if content_info['type'] == 'video':
                await message.reply_video(
                    video=content_info['file_path'],
                    caption=f"📹 {content_info['title']}",
                    duration=content_info.get('duration', 0),
                    thumb=content_info.get('thumbnail')
                )
            else:
                await message.reply_document(
                    document=content_info['file_path'],
                    caption=f"📄 {content_info['title']}"
                )

if __name__ == "__main__":
    logger.info("Starting Advanced Course Portal Bot...")
    app.run()
