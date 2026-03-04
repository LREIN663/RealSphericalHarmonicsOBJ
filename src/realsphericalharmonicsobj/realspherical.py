#!/usr/bin/env python3
"""
Real Spherical Harmonics OBJ Exporter

This script generates 3D mesh files (.obj) of real spherical harmonics
or linear combinations thereof, colored by the sign of the harmonic values.
"""

import argparse
import os
import numpy as np
import trimesh

from scipy.special import sph_harm

def create_spherical_grid(n_theta=100, n_phi=100):
    """Create a spherical grid for evaluating spherical harmonics.
    
    Parameters:
    -----------
    n_theta : int
        Number of points in the polar angle direction
    n_phi : int
        Number of points in the azimuthal angle direction
        
    Returns:
    --------
    theta : ndarray
        Polar angles (0 to pi)
    phi : ndarray
        Azimuthal angles (0 to 2*pi)
    xyz : ndarray
        Unit sphere coordinates in Cartesian form
    """
    theta = np.linspace(0, np.pi, n_theta)
    phi = np.linspace(0, 2*np.pi, n_phi)
    theta, phi = np.meshgrid(theta, phi)
    
    # Calculate the Cartesian coordinates of each point on the unit sphere
    xyz = np.array([np.sin(theta) * np.sin(phi),
                    np.sin(theta) * np.cos(phi),
                    np.cos(theta)])
    return theta, phi, xyz


def compute_real_spherical_harmonic(l, m, theta, phi):
    """Compute real spherical harmonic Y_l^m.
    
    Parameters:
    -----------
    l : int
        Degree of the spherical harmonic
    m : int
        Order of the spherical harmonic (-l <= m <= l)
    theta : ndarray
        Polar angles (0 to pi)
    phi : ndarray
        Azimuthal angles (0 to 2*pi)
        
    Returns:
    --------
    Y : ndarray
        Real spherical harmonic values
    """
    # scipy.special.sph_harm uses the physics convention:
    # sph_harm(m, l, phi, theta) where phi is azimuthal and theta is polar
    # Y = sph_harm(abs(m), l, phi, theta)
    Yc = sph_harm(m, l, phi, theta)  # NOTE: m (can be negative) and order phi,theta

    if m > 0:
        return np.sqrt(2) * (-1) ** m * Yc.real
    elif m < 0:
        return np.sqrt(2) * (-1) ** m * Yc.imag
    else:
        return Yc.real


def export_spherical_harmonic(l, m, filename, n_theta=100, n_phi=100,
                              color_positive=(1.0, 0.0, 0.0),
                              color_negative=(0.0, 0.0, 1.0)):
    """Export a single real spherical harmonic as an OBJ file.
    
    Parameters:
    -----------
    l : int
        Degree of the spherical harmonic
    m : int
        Order of the spherical harmonic (-l <= m <= l)
    filename : str
        Output filename (should end in .obj)
    n_theta : int
        Number of points in the polar direction
    n_phi : int
        Number of points in the azimuthal direction
    color_positive : tuple
        RGB color for positive values (default: red)
    color_negative : tuple
        RGB color for negative values (default: blue)
    """
    theta, phi, xyz = create_spherical_grid(n_theta, n_phi)
    Y = compute_real_spherical_harmonic(l, m, theta, phi)
    
    # Scale the unit sphere by the absolute value of the harmonic
    Yx, Yy, Yz = np.abs(Y) * xyz
    
    export_to_obj_with_colors(Yx, Yy, Yz, Y, filename,
                             color_positive, color_negative)


def export_superposition(factors, filename, n_theta=100, n_phi=100,
                        color_positive=(1.0, 0.0, 0.0),
                        color_negative=(0.0, 0.0, 1.0)):
    """Export a linear combination of real spherical harmonics as an OBJ file.
    
    Parameters:
    -----------
    factors : list of tuples
        Each tuple contains (l, m, coefficient) where l is the degree,
        m is the order, and coefficient is the weight for that harmonic
    filename : str
        Output filename (should end in .obj)
    n_theta : int
        Number of points in the polar direction
    n_phi : int
        Number of points in the azimuthal direction
    color_positive : tuple
        RGB color for positive values (default: red)
    color_negative : tuple
        RGB color for negative values (default: blue)
    """
    theta, phi, xyz = create_spherical_grid(n_theta, n_phi)
    Y_total = np.zeros_like(theta, dtype=float)
    
    for l, m, coefficient in factors:
        Y = compute_real_spherical_harmonic(l, m, theta, phi)
        Y_total += coefficient * Y
    
    # Scale the unit sphere by the absolute value of the total
    Yx, Yy, Yz = np.abs(Y_total) * xyz
    
    export_to_obj_with_colors(Yx, Yy, Yz, Y_total, filename,
                             color_positive, color_negative)


def export_to_obj_with_colors(Yx, Yy, Yz, Y_values, filename,
                              color_positive=(1.0, 0.0, 0.0),
                              color_negative=(0.0, 0.0, 1.0)):
    """Export a 3D mesh as an OBJ file with vertex colors based on sign.
    
    Parameters:
    -----------
    Yx, Yy, Yz : ndarray
        Coordinates of the vertices (2D grids)
    Y_values : ndarray
        Values used for coloring based on sign
    filename : str
        Output filename (should end in .obj)
    color_positive : tuple
        RGB color for positive values (default: red = (1.0, 0.0, 0.0))
    color_negative : tuple
        RGB color for negative values (default: blue = (0.0, 0.0, 1.0))
    """
    # Collect vertices from the 2D grid
    vertices = np.column_stack((Yx.ravel(), Yy.ravel(), Yz.ravel()))
    
    # Create triangular faces from the grid structure
    faces = []
    for i in range(Yx.shape[0] - 1):
        for j in range(Yx.shape[1] - 1):
            # Two triangles per quad cell
            v1 = i * Yx.shape[1] + j
            v2 = i * Yx.shape[1] + j + 1
            v3 = (i + 1) * Yx.shape[1] + j + 1
            v4 = (i + 1) * Yx.shape[1] + j
            faces.append([v1, v2, v3])
            faces.append([v1, v3, v4])

    faces = np.array(faces)
    
    # Assign colors based on sign
    vertex_colors = np.zeros((Y_values.size, 3))
    Y_flat = Y_values.ravel()
    vertex_colors[Y_flat >= 0] = color_positive
    vertex_colors[Y_flat < 0] = color_negative
    
    # Create and export the mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=vertex_colors)
    mesh.export(filename)
    print(f"Exported: {filename}")


def parse_color(color_str):
    """Parse a color string in R,G,B format.
    
    Parameters:
    -----------
    color_str : str
        Color in format "R,G,B" where values are 0-1 or 0-255
        
    Returns:
    --------
    tuple : (R, G, B) with values normalized to 0-1
    """
    try:
        parts = color_str.split(',')
        if len(parts) != 3:
            raise ValueError(f"Color must have 3 components (got {len(parts)})")
        
        r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
        
        # If any value is > 1, assume 0-255 range and normalize
        if r > 1.0 or g > 1.0 or b > 1.0:
            r, g, b = r / 255.0, g / 255.0, b / 255.0
        
        # Validate range
        if not (0 <= r <= 1 and 0 <= g <= 1 and 0 <= b <= 1):
            raise ValueError("Color values must be in range 0-1 or 0-255")
        
        return (r, g, b)
    except Exception as e:
        print(f"Error parsing color '{color_str}': {e}")
        print("Using default color instead")
        return None


def run_examples(output_dir="output"):
    """Run built-in examples."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Example 1: Export individual spherical harmonics
    print("Exporting individual spherical harmonics...")
    export_spherical_harmonic(l=2, m=0, filename=os.path.join(output_dir, "Y_2_0.obj"))
    export_spherical_harmonic(l=3, m=-2, filename=os.path.join(output_dir, "Y_3_-2.obj"))
    
    # Example 2: Export linear combinations (superpositions)
    # These represent f-orbital-like shapes
    print("Exporting f-orbital-like superpositions...")
    strc = [
        [-0.58415, -0.17274, 0.55493, 0.17169, 0.53062, -0.08398, 0.05378],
        [-0.44353, -0.30348, 0.07170, -0.05691, -0.62627, -0.21859, -0.51264]
    ]
    for idx, coefficients in enumerate(strc, 1):
        factors = [(3, m, coeff) for m, coeff in enumerate(coefficients, start=-3)]
        export_superposition(factors, os.path.join(output_dir, f"strc_{idx}.obj"))
    
    print(f"\nAll examples exported to {output_dir}/")


def main():
    """Command-line interface for spherical harmonic export."""
    parser = argparse.ArgumentParser(
        description="Export real spherical harmonics as OBJ mesh files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export a single harmonic Y_2^0
  %(prog)s --single 2 0 --output Y_2_0.obj
  
  # Export multiple harmonics
  %(prog)s --single 2 0 --single 3 -2 --single 3 2
  
  # Export a linear combination
  %(prog)s --combo "3,-3,0.5" "3,-2,0.3" "3,0,0.7" --output combo.obj
  
  # Custom colors (green for positive, magenta for negative)
  %(prog)s --single 2 0 --color-positive "0,1,0" --color-negative "1,0,1"
  
  # Using 0-255 RGB values
  %(prog)s --single 3 2 --cp "255,165,0" --cn "128,0,128"
  
  # Run built-in examples
  %(prog)s --examples
  
  # High resolution mesh
  %(prog)s --single 2 0 --resolution 200
        """)
    
    parser.add_argument('--single', nargs=2, metavar=('L', 'M'), action='append',
                        help='Export single harmonic Y_l^m (can be used multiple times)')
    parser.add_argument('--combo', nargs='+', metavar='L,M,COEFF',
                        help='Export linear combination of harmonics (format: "l,m,coeff")')
    parser.add_argument('--output', '-o', 
                        help='Output filename (for single harmonic or combination)')
    parser.add_argument('--output-dir', default='output',
                        help='Output directory (default: output/)')
    parser.add_argument('--resolution', '-r', type=int, default=100,
                        help='Mesh resolution (default: 100)')
    parser.add_argument('--color-positive', '--cp', metavar='R,G,B',
                        help='Color for positive values as R,G,B (0-1 or 0-255), e.g., "1,0,0" for red')
    parser.add_argument('--color-negative', '--cn', metavar='R,G,B',
                        help='Color for negative values as R,G,B (0-1 or 0-255), e.g., "0,0,1" for blue')
    parser.add_argument('--examples', action='store_true',
                        help='Run built-in examples')
    
    args = parser.parse_args()
    
    # Parse colors
    color_positive = (1.0, 0.0, 0.0)  # Default: red
    color_negative = (0.0, 0.0, 1.0)  # Default: blue
    
    if args.color_positive:
        parsed = parse_color(args.color_positive)
        if parsed:
            color_positive = parsed
    
    if args.color_negative:
        parsed = parse_color(args.color_negative)
        if parsed:
            color_negative = parsed
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run examples if requested
    if args.examples:
        run_examples(args.output_dir)
        return
    
    # Export single harmonics
    if args.single:
        for i, (l_str, m_str) in enumerate(args.single):
            l, m = int(l_str), int(m_str)
            
            # Check validity
            if l < 0:
                print(f"Error: l must be non-negative (got l={l})")
                continue
            if abs(m) > l:
                print(f"Error: |m| must be ≤ l (got l={l}, m={m})")
                continue
            
            # Determine filename
            if args.output and len(args.single) == 1:
                filename = args.output
            else:
                filename = f"Y_{l}_{m}.obj"
            
            if not os.path.isabs(filename):
                filename = os.path.join(args.output_dir, filename)
            
            export_spherical_harmonic(l, m, filename, 
                                     n_theta=args.resolution, 
                                     n_phi=args.resolution,
                                     color_positive=color_positive,
                                     color_negative=color_negative)
    
    # Export combination
    if args.combo:
        factors = []
        for spec in args.combo:
            try:
                parts = spec.split(',')
                if len(parts) != 3:
                    print(f"Error: combo format should be 'l,m,coeff' (got '{spec}')")
                    return
                l, m, coeff = int(parts[0]), int(parts[1]), float(parts[2])
                factors.append((l, m, coeff))
            except ValueError as e:
                print(f"Error parsing combo '{spec}': {e}")
                return
        
        # Determine filename
        if args.output:
            filename = args.output
        else:
            filename = "combination.obj"
        
        if not os.path.isabs(filename):
            filename = os.path.join(args.output_dir, filename)
        
        export_superposition(factors, filename,
                           n_theta=args.resolution,
                           n_phi=args.resolution,
                           color_positive=color_positive,
                           color_negative=color_negative)
    
    # If no arguments provided, show help
    if not (args.single or args.combo or args.examples):
        parser.print_help()


if __name__ == "__main__":
    main()
