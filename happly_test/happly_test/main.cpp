#include <iostream>
#include "happly.h"
#include <string>
#include <ranges>

int main() {
    // Construct a data object by reading from file
    happly::PLYData plyIn("dummy_ascii.ply");

    // Get data from the object
    std::vector<double> element_vertex_x_coords = plyIn.getElement("vertex").getProperty<double>("x");
    std::vector<double> element_vertex_y_coords = plyIn.getElement("vertex").getProperty<double>("y");
    std::vector<double> element_vertex_z_coords = plyIn.getElement("vertex").getProperty<double>("z");
    std::vector<double> element_vertex_inner_dists = plyIn.getElement("vertex").getProperty<double>("inner_dist");
    std::vector<double> element_vertex_outer_dists = plyIn.getElement("vertex").getProperty<double>("outer_dist");
    std::vector<int> element_gaussian_indices = plyIn.getElement("gaussian_index").getProperty<int>("i");
    std::vector<std::vector<double>> element_gaussian_bary_coords = plyIn.getElement("gaussian_bary_coords").getListProperty<double>("bary_coords");
    
    // Print 10 vertices
    size_t count = std::min<size_t>(10, element_vertex_x_coords.size());
    for (size_t i = 0; i < count; ++i) {
        std::cout << "Vertex " << i + 1 << ": (" << element_vertex_x_coords[i] << ", " << element_vertex_y_coords[i] << ", " << element_vertex_z_coords[i] << ") " << "FrostingBounds: " << "(" << element_vertex_inner_dists[i] << ", " << element_vertex_outer_dists[i] << ") " << std::endl;
    }

    // Print 10 indices
    count = std::min<size_t>(10, element_gaussian_indices.size());
    for (size_t i = 0; i < count; ++i) {
        std::cout << "Gaussian Index " << i + 1 << ": " << element_gaussian_indices[i] << std::endl;
    }

    // Print 10 bary coord lists
    count = std::min<size_t>(10, element_gaussian_bary_coords.size());
    for (size_t i = 0; i < count; ++i) {
        std::string bary_coords_str = "(";
        // Join the barycentric coordinates into a single string
        for (size_t j = 0; j < element_gaussian_bary_coords[i].size(); ++j) {
            bary_coords_str += std::to_string(element_gaussian_bary_coords[i][j]);
            if (j < element_gaussian_bary_coords[i].size() - 1) {
                bary_coords_str += ", ";
            }
            else
            {
                bary_coords_str += "";
            }
        }
        bary_coords_str += ")";
        std::cout << "Gaussian " << i << " BaryCoords: " << bary_coords_str << std::endl;
    }

    return 0;
}