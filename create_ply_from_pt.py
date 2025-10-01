import torch
import numpy as np
import struct

def create_ply_from_pt(checkpoint_path, ply_path, use_binary_format=False, vertices_lim=None, faces_lim=None, gaussians_lim=None):
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
    num_vertices = min(vertices.shape[0], vertices_lim) if vertices_lim is not None else vertices.shape[0]
    num_faces = min(faces.shape[0], faces_lim) if faces_lim is not None else faces.shape[0]
    num_gaussians = min(point_cell_indices.shape[0], gaussians_lim) if gaussians_lim is not None else point_cell_indices.shape[0]
    
    format_type = 'binary_little_endian 1.0' if use_binary_format else 'ascii 1.0'

    header = f"""ply
format {format_type}
comment mesh vertices and frosting layer bounds
element vertex {num_vertices}
property double x
property double y
property double z
property double outer_dist
property double inner_dist
element face {num_faces}
property list uchar uint vertex_indices
comment gaussians and their properties
element gaussian_index {num_gaussians}
property int i
element gaussian_bary_coords {num_gaussians}
property list uchar double bary_coords
element gaussian_scales {num_gaussians}
property list uchar float scales
element gaussian_quaternions {num_gaussians}
property list uchar double quaternions
element gaussian_opacity {num_gaussians}
property double opacity
comment spherical harmonics coefficients
element gaussian_sh_dc {num_gaussians}
property list uchar float sh_dc_coordinates
element gaussian_sh_rest {num_gaussians}
property list uchar double sh_rest_coordinates
end_header
"""
    if use_binary_format:
        # Write binary PLY file
        with open(ply_path, 'wb') as ply_file:
            # Write ASCII header
            ply_file.write(header.encode('utf-8'))
            
            # Write vertex data (binary)
            for i in range(num_vertices):
                ply_file.write(struct.pack('<ddddd', vertices[i][0], vertices[i][1], vertices[i][2], 
                                          outer_dist[i], inner_dist[i]))
            
            # Write face data (binary)
            for i in range(num_faces):
                ply_file.write(struct.pack('<B', faces[i].shape[0]))  # count as uchar
                for j in range(faces[i].shape[0]):
                    ply_file.write(struct.pack('<I', faces[i][j]))  # indices as uint
            
            # Write gaussian indices
            for i in range(num_gaussians):
                ply_file.write(struct.pack('<i', point_cell_indices[i]))
            
            # Write bary coords
            for i in range(num_gaussians):
                ply_file.write(struct.pack('<B', len(bary_coords[i])))
                for val in bary_coords[i]:
                    ply_file.write(struct.pack('<d', val))
            
            # Write scales
            for i in range(num_gaussians):
                ply_file.write(struct.pack('<B', len(scales[i])))
                for val in scales[i]:
                    ply_file.write(struct.pack('<f', val))
            
            # Write quaternions
            for i in range(num_gaussians):
                ply_file.write(struct.pack('<B', len(quaternions[i])))
                for val in quaternions[i]:
                    ply_file.write(struct.pack('<d', val))
            
            # Write opacity
            for i in range(num_gaussians):
                ply_file.write(struct.pack('<d', opacities[i][0]))
            
            # Write sh_coordinates_dc
            for i in range(num_gaussians):
                ply_file.write(struct.pack('<B', len(sh_coordinates_dc[i][0])))
                for val in sh_coordinates_dc[i][0]:
                    ply_file.write(struct.pack('<f', val))
            
            # Write sh_coordinates_rest
            for i in range(num_gaussians):
                ply_file.write(struct.pack('<B', len(sh_coordinates_rest_unpacked[i])))
                for val in sh_coordinates_rest_unpacked[i]:
                    ply_file.write(struct.pack('<d', val))
        
        print(f"Binary PLY file saved to {ply_path}")
    else:
        # Write ASCII PLY file
        content = header
        
        # Add vertex data
        for i in range(num_vertices):
            content += f"{vertices[i][0]} {vertices[i][1]} {vertices[i][2]} {outer_dist[i]} {inner_dist[i]}\n"
        
        # Add face data
        for i in range(num_faces):
            content += f"{faces[i].shape[0]} {faces[i][0]} {faces[i][1]} {faces[i][2]}\n"
        
        # Add per splat data
        for i in range(num_gaussians):
            content += f"{point_cell_indices[i]}\n"
        
        # Add bary coords
        for i in range(num_gaussians):
            bary_coords_list_str = ' '.join(map(str, bary_coords[i]))
            content += f"{len(bary_coords[i])} {bary_coords_list_str}\n"
        
        # Add scales
        for i in range(num_gaussians):
            scale_list_str = ' '.join(map(str, scales[i]))
            content += f"{len(scales[i])} {scale_list_str}\n"
        
        # Add quaternions
        for i in range(num_gaussians):
            quaternion_list_str = ' '.join(map(str, quaternions[i]))
            content += f"{len(quaternions[i])} {quaternion_list_str}\n"
        
        # Add opacity
        for i in range(num_gaussians):
            content += f"{opacities[i][0]}\n"
        
        # Add sh_coordinates
        for i in range(num_gaussians):
            sh_dc_list_str = ' '.join(map(str, sh_coordinates_dc[i][0]))
            content += f"{len(sh_coordinates_dc[i][0])} {sh_dc_list_str}\n"
        
        # Add sh_coordinates_rest
        for i in range(num_gaussians):
            sh_rest_list_str = ' '.join(map(str, sh_coordinates_rest_unpacked[i]))
            content += f"{len(sh_coordinates_rest_unpacked[i])} {sh_rest_list_str}\n"
        
        with open(ply_path, 'w') as ply_file:
            ply_file.write(content)
        print(f"ASCII PLY file saved to {ply_path}")

create_ply_from_pt('dummy.pt', 'dummy_ascii.ply', False, 10, 10, 10)
create_ply_from_pt('dummy.pt', 'dummy_bin.ply', True, 10, 10, 10)
