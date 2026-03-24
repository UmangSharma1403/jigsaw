# Jigsaw - Image to Bead Art Converter

This project converts images into bead art mosaics using a deep learning-based color quantization approach. It identifies the main subject, matches colors to a bead palette, and generates a high-resolution grid representation.

## Features

- **Smart Cropping**: Detects faces (portraits) or main subjects (saliency) to focus on the most important part of the image
- **Color Quantization**: Uses K-Nearest Neighbors (KNN) in LAB color space for perceptually accurate color matching
- **Bead Palette**: Matches colors to a curated palette of 100 bead colors
- **High-Resolution Output**: Generates 1000x1000 pixel bead art grids
- **Grid Overlay**: Adds a visible grid to the output for a realistic bead pattern look

## Setup

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd jigsaw
    ```

2.  **Create a virtual environment**
    ```bash
    python3 -m venv ven
    source ven/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Command Line Interface

The script includes a CLI for easy image processing:

```bash
python app/main.py --image <path_to_image> --output <output_path>
```

**Example:**

```bash
python app/main.py --image assets/test.jpg --output output/test_bead_art.png
```

### API Usage

You can also use the API by running:

```bash
uvicorn app.main:app --reload
```

Then send POST requests to `/convert` with the image:

```bash
curl -X POST "http://localhost:8000/convert" \
     -H "Content-Type: application/json" \
     -d '{"image_url": "https://example.com/image.jpg"}'
```

## Project Structure

```
jigsaw/
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── processor.py     # Image processing pipeline
│   ├── palette.py       # Bead color palette definitions
│   └── utils.py         # Utility functions
├── assets/              # Sample images (for testing)
├── output/              # Generated bead art images
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Development

### Adding New Beads

To add new bead colors, update the `BEAD_PALETTE` list in `app/palette.py`. The palette should contain RGB tuples (0-255).

### Testing

Run the CLI with a test image:

```bash
python app/main.py --image assets/test.jpg --output output/test_bead_art.png
```

## License

MIT License
