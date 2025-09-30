import torch
import numpy as np
import struct

def export_frosting_checkpoint_to_binary_ply(checkpoint_path, ply_path):
    # Load the checkpoint
    model = torch.load(checkpoint_path, weights_only=False)

    # Extract the state_dict (assume the model is stored as state_dict in the checkpoint)
    if isinstance(model, dict) and 'state_dict' in model:
        model = model['state_dict']

    # Extract the required components
    # Vertex elements (3D coordinates)
    vertices = model['_shell_base_verts'].cpu().detach().numpy()
    outer_dist = model['_outer_dist'].cpu().detach().numpy()
    inner_dist = model['_inner_dist'].cpu().detach().numpy()

    # Face elements (indices)
    faces = model['_shell_base_faces'].cpu().detach().numpy()

    # Gaussian splat elements (properties like cell indices, bary coordinates, scale, etc.)
    point_cell_indices = model['_point_cell_indices'].cpu().detach().numpy()
    bary_coords = model['_bary_coords'].cpu().detach().numpy()
    scales = model['_scales'].cpu().detach().numpy()
    quaternions = model['_quaternions'].cpu().detach().numpy()
    opacities = model['_opacities'].cpu().detach().numpy()
    sh_coordinates_dc = model['_sh_coordinates_dc'].cpu().detach().numpy()
    sh_coordinates_rest = model['_sh_coordinates_rest'].cpu().detach().numpy()

    # Unpack _sh_coordinates_rest (contains 15 arrays of 3 elements each)
    sh_coordinates_rest_unpacked = []
    for i in range(sh_coordinates_rest.shape[0]):
        # Unpack each row of 15 arrays of 3 elements
        unpacked = []
        for j in range(15):
            unpacked.extend(sh_coordinates_rest[i][j])
        sh_coordinates_rest_unpacked.append(unpacked)
    sh_coordinates_rest_unpacked = np.array(sh_coordinates_rest_unpacked)

    # PLY header
    num_vertices = vertices.shape[0]
    num_faces = faces.shape[0]
    num_gaussians = point_cell_indices.shape[0]
    
    header = f"""ply
format ascii 1.0
comment mesh vertices and frosting layer bounds
element vertex {num_vertices}
property float32 x
property float32 y
property float32 z
property float32 outer_dist
property float32 inner_dist
comment mesh faces
element face {num_faces}
comment type following 'list' is size type
property list uint8 int32 vertex_indices
comment gaussians by index and their properties
element gaussian {num_gaussians}
property int32 i
property list uint8 float32 bary_coords
property list uint8 float32 scale
property list uint8 float32 quaternion
property float32 opacity
comment spherical harmonics coefficients
property list uint8 float32 sh_coordinates_dc
property list uint8 float32 sh_coordinates_rest
end_header
"""

    # Writing to PLY file in little-endian binary format
    # Open the file in binary write mode
    with open(ply_path, 'wb') as ply_file:
        # Write header
        ply_file.write(header.encode('utf-8'))
        ply_file.write(b'\n')  # Ensure there's a newline after the header
        # Write vertex data
        for i in range(num_vertices):
            ply_file.write(struct.pack('<5f', vertices[i][0], vertices[i][1], vertices[i][2], outer_dist[i], inner_dist[i]))
        # Write face data
        for i in range(num_faces):
            ply_file.write(struct.pack('<3i', faces[i][0], faces[i][1], faces[i][2]))  # '3' indicates a triangle
        # Write per splat data
        for i in range(num_gaussians):
            # Write index
            ply_file.write(struct.pack('<i', point_cell_indices[i]))
            # Write bary_coords (6 floats)
            ply_file.write(struct.pack('<6f', *bary_coords[i]))  # '6' indicates three floats
            # Write scale (3 floats)
            ply_file.write(struct.pack('<3f', *scales[i]))  # '3' indicates three floats
            # Write quaternion (4 floats)
            ply_file.write(struct.pack('<4f', *quaternions[i]))  # '4' indicates four floats
            # Write opacity (1 float)
            ply_file.write(struct.pack('<f', opacities[i][0]))
            # Write sh_coordinates_dc (3 floats)
            ply_file.write(struct.pack('<3f', *sh_coordinates_dc[i][0]))  # '3' indicates three floats
            # Write sh_coordinates_rest (45 floats)
            ply_file.write(struct.pack('<45f', *sh_coordinates_rest_unpacked[i]))  # '45' indicates forty-five floats            

    print(f"PLY file saved to {ply_path}")

export_frosting_checkpoint_to_binary_ply('15000.pt', 'export_bin.ply')
