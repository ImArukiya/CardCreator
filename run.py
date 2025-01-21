import os
import curses
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Define the folder containing the font files
FONT_FOLDER = "Data/Fonts"

# Define the folder to save images
PICTURES_FOLDER = os.path.join(os.getcwd(), "Pictures")

# Define color options (including basic colors and extended colors)
COLOR_OPTIONS = [
    ("Black", (0, 0, 0)),
    ("Red", (255, 0, 0)),
    ("Green", (0, 255, 0)),
    ("Yellow", (255, 255, 0)),
    ("Blue", (0, 0, 255)),
    ("Magenta", (255, 0, 255)),
    ("Cyan", (0, 255, 255)),
    ("White", (255, 255, 255)),
    ("Gray", (169, 169, 169)),  # Simulating gray with RGB
]

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None  # Return None if invalid hex color

def ensure_pictures_folder():
    if not os.path.exists(PICTURES_FOLDER):
        os.makedirs(PICTURES_FOLDER)
    return PICTURES_FOLDER

def get_font_files(font_folder):
    fonts = []
    for file in os.listdir(font_folder):
        if file.endswith(".ttf"):
            fonts.append({"name": os.path.splitext(file)[0], "path": os.path.join(font_folder, file)})
    return fonts

def get_optimal_font_size(draw, text, font_path, max_width, max_height, start_size=100):
    font_size = start_size
    while True:
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if text_width <= max_width and text_height <= max_height:
            return font
        font_size -= 1

def display_menu(stdscr, options, title="Menu"):
    curses.curs_set(0)
    current_row = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, title, curses.color_pair(1))

        for idx, option in enumerate(options):
            x = 2
            y = idx + 2
            if idx == current_row:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(y, x, option)
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.addstr(y, x, option)

        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return current_row

def create_card(selected_font_path, title, description, times, border_color, background_color, text_color, additional_texts=[]):
    card_width, card_height = 3000, 1812
    card = Image.new("RGB", (card_width, card_height), background_color)
    draw = ImageDraw.Draw(card)

    title_max_width = card_width * 0.9
    title_max_height = card_height * 0.3
    desc_max_width = card_width * 0.9
    desc_max_height = card_height * 0.2

    try:
        title_font = get_optimal_font_size(draw, title, selected_font_path, title_max_width, title_max_height, start_size=150)
        desc_font = get_optimal_font_size(draw, description, selected_font_path, desc_max_width, desc_max_height, start_size=80)
    except OSError:
        print(f"Font {selected_font_path} not found. Using default font.")
        title_font = ImageFont.load_default()
        desc_font = ImageFont.load_default()

    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    desc_bbox = draw.textbbox((0, 0), description, font=desc_font)

    title_width, title_height = title_bbox[2] - title_bbox[0], title_bbox[3] - title_bbox[1]
    desc_width, desc_height = desc_bbox[2] - desc_bbox[0], desc_bbox[3] - desc_bbox[1]

    title_x = (card_width - title_width) // 2
    title_y = (card_height - title_height) // 2 - 100

    desc_x = (card_width - desc_width) // 2
    desc_y = (card_height - desc_height) // 2 + 100

    # Apply text color (now RGB format)
    draw.text((title_x, title_y), title, fill=text_color, font=title_font)
    draw.text((desc_x, desc_y), description, fill=text_color, font=desc_font)

    for additional_text in additional_texts:
        additional_font = ImageFont.load_default()
        additional_text_bbox = draw.textbbox((0, 0), additional_text, font=additional_font)
        additional_width, additional_height = additional_text_bbox[2] - additional_text_bbox[0], additional_text_bbox[3] - additional_text_bbox[1]
        additional_x = (card_width - additional_width) // 2
        additional_y = card_height - additional_height - 40
        draw.text((additional_x, additional_y), additional_text, fill=text_color, font=additional_font)

    # Border color and border width
    if border_color:
        border_width = 20
        draw.rectangle([border_width, border_width, card_width - border_width, card_height - border_width], outline=border_color, width=border_width)

    times_text = f"Times: {times}"
    times_font = ImageFont.load_default()
    times_bbox = draw.textbbox((0, 0), times_text, font=times_font)
    times_width, times_height = times_bbox[2] - times_bbox[0], times_bbox[3] - times_bbox[1]
    times_x = (card_width - times_width) // 2
    times_y = card_height - times_height - 20

    draw.text((times_x, times_y), times_text, fill=text_color, font=times_font)

    output_path = os.path.join(PICTURES_FOLDER, "card.jpg")
    card.save(output_path, "JPEG")
    print(f"Card saved as {output_path}")

def delete_card():
    ensure_pictures_folder()
    card_path = os.path.join(PICTURES_FOLDER, "card.jpg")
    if os.path.exists(card_path):
        os.remove(card_path)
        print(f"Deleted {card_path}")
    else:
        print(f"No card found in {PICTURES_FOLDER}")

def select_color(stdscr, color_type):
    options = [color[0] for color in COLOR_OPTIONS] + ["Custom Hex Color"]
    selected_color_idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Select {color_type} Color", curses.color_pair(1))
        for idx, option in enumerate(options):
            x = 2
            y = idx + 2
            if idx == selected_color_idx:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(y, x, option)
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.addstr(y, x, option)

        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and selected_color_idx > 0:
            selected_color_idx -= 1
        elif key == curses.KEY_DOWN and selected_color_idx < len(options) - 1:
            selected_color_idx += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if selected_color_idx == len(options) - 1:  # Custom Hex Color
                stdscr.clear()
                stdscr.addstr(0, 0, "Enter hex color (e.g., #FF5733): ", curses.color_pair(1))
                curses.echo()
                hex_color = stdscr.getstr(1, 0, 7).decode("utf-8")
                curses.noecho()
                rgb_color = hex_to_rgb(hex_color)
                if rgb_color:
                    return rgb_color
                else:
                    stdscr.addstr(3, 0, "Invalid hex code. Try again.")
                    stdscr.refresh()
                    stdscr.getch()
            else:
                return COLOR_OPTIONS[selected_color_idx][1]

def create_card_menu(stdscr, fonts):
    card_title = ""
    card_desc = ""
    selected_font = fonts[0]
    times = 1
    border_color = (0, 0, 0)  # Default border color (black)
    background_color = (255, 255, 255)  # Default background color (white)
    text_color = (0, 0, 0)  # Default text color (black)
    additional_texts = []
    
    while True:
        options = [
            f"Set Name • {card_title or 'Not Set'}",
            f"Set Desc • {card_desc or 'Not Set'}",
            f"Select Font • {selected_font['name']}",
            f"How Many Times • {times}",
            f"Border Color • {border_color}",
            f"Background Color • {background_color}",
            f"Text Color • {text_color}",
            "Add Additional Text",
            "Preview Card",
            "Create Card"
        ]
        choice = display_menu(stdscr, options, title="Card Configuration")

        if choice == 0:  # Set Name
            stdscr.clear()
            stdscr.addstr(0, 0, "Enter the title: ", curses.color_pair(1))
            curses.echo()
            card_title = stdscr.getstr(1, 0, 50).decode("utf-8")
            curses.noecho()
        elif choice == 1:  # Set Description
            stdscr.clear()
            stdscr.addstr(0, 0, "Enter the description: ", curses.color_pair(1))
            curses.echo()
            card_desc = stdscr.getstr(1, 0, 100).decode("utf-8")
            curses.noecho()
        elif choice == 2:  # Select Font
            font_options = [font["name"] for font in fonts]
            font_choice = display_menu(stdscr, font_options, title="Select a Font")
            selected_font = fonts[font_choice]
        elif choice == 3:  # How Many Times
            times_options = ["1", "2", "3", "5", "10", "Unlimited"]
            times_choice = display_menu(stdscr, times_options, title="Select How Many Times")
            times = int(times_options[times_choice]) if times_options[times_choice] != "Unlimited" else "Unlimited"
        elif choice == 4:  # Border Color
            border_color = select_color(stdscr, "Border")
        elif choice == 5:  # Background Color
            background_color = select_color(stdscr, "Background")
        elif choice == 6:  # Text Color
            text_color = select_color(stdscr, "Text")
        elif choice == 7:  # Add Additional Text
            stdscr.clear()
            stdscr.addstr(0, 0, "Enter additional text: ", curses.color_pair(1))
            curses.echo()
            additional_text = stdscr.getstr(1, 0, 50).decode("utf-8")
            additional_texts.append(additional_text)
            curses.noecho()
        elif choice == 8:  # Preview Card
            create_card(selected_font["path"], card_title, card_desc, times, border_color, background_color, text_color, additional_texts)
            stdscr.clear()
            stdscr.addstr(0, 0, "Card Previewed! Press any key to continue.", curses.color_pair(1))
            stdscr.refresh()
            stdscr.getch()
        elif choice == 9:  # Create Card
            if card_title and card_desc:  # Ensure title and description are set
                create_card(selected_font["path"], card_title, card_desc, times, border_color, background_color, text_color, additional_texts)
                break

def main_menu(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

    fonts = get_font_files(FONT_FOLDER)

    while True:
        main_options = ["Create Card", "Delete Card", "Exit"]
        choice = display_menu(stdscr, main_options, title="Main Menu")

        if choice == 0:  # Create Card
            create_card_menu(stdscr, fonts)
        elif choice == 1:  # Delete Card
            delete_card()
        elif choice == 2:  # Exit
            break


if __name__ == "__main__":
    curses.wrapper(main_menu)
