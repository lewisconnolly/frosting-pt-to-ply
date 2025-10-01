# Create ply file from Frosting PyTorch checkpoint

## ℹ️ Overview

A Python utility to convert PyTorch checkpoint files (.pt) containing Frosting model data into PLY (Polygon File Format) files. Supports both ASCII and binary PLY formats for efficient storage and visualization of 3D mesh data with Gaussian splatting properties.

## ❔ Context
Used to create ply from [Frosting](https://github.com/Anttwo/Frosting) data. Frosting is a method for representing 3D scenes using Gaussian splatting on mesh surfaces. This tool extracts mesh geometry, Gaussian splat parameters, and spherical harmonics coefficients from trained model checkpoints.

## 🌟 Features

- Converts PyTorch checkpoint files to PLY format
- Supports both ASCII and binary PLY output formats
- Extracts mesh vertices with outer/inner distance properties
- Exports face indices for mesh topology
- Preserves Gaussian splatting parameters:
  - Cell indices and barycentric coordinates
  - Scale and rotation (quaternions)
  - Opacity values
  - Spherical harmonics coefficients (DC and rest)
- Optional limiting of vertices, faces, and Gaussians for testing

## ⬇️ Installation

Download the script:

```bash
git clone https://github.com/yourusername/frosting-pt-to-ply.git
cd frosting-pt-to-ply
```

**Requirements:**
- Python 3.x
- PyTorch
- NumPy

Install dependencies:
```bash
pip install torch numpy
```

## 💻 Usage

```python
from create_ply_from_pt import create_ply_from_pt

# Create ASCII PLY file
create_ply_from_pt('model.pt', 'output_ascii.ply', use_binary_format=False)

# Create binary PLY file (more compact)
create_ply_from_pt('model.pt', 'output_binary.ply', use_binary_format=True)

# Limit output for testing (10 vertices, 10 faces, 10 Gaussians)
create_ply_from_pt('model.pt', 'output_test.ply', use_binary_format=False,
                   vertices_lim=10, faces_lim=10, gaussians_lim=10)
```

**Parameters:**
- `checkpoint_path`: Path to the PyTorch checkpoint file (.pt)
- `ply_path`: Output path for the PLY file
- `use_binary_format`: Boolean, True for binary format, False for ASCII (default: False)
- `vertices_lim`: Optional limit on number of vertices to export
- `faces_lim`: Optional limit on number of faces to export
- `gaussians_lim`: Optional limit on number of Gaussian splats to export

## Testing

The `happly_test` directory contains a Visual Studio solution for testing the generated PLY files using the [happly](https://github.com/nmwsharp/happly) C++ library. This ensures the PLY files are correctly formatted and can be read by standard PLY parsers.
