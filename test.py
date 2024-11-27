import numpy as np
import matplotlib.pyplot as plt

# Given weights and bias
w11, w21 = 1, -2
w12, w22 = -3, 1
b = -1

# Define the ReLU function
def relu(x):
    return np.maximum(0, x)

# def z1(x1,x2):
#     return relu(w11 * x1 + w21 * x2)

# def z2(x1,x2):
#     return relu(w12 * x1 + w22 * x2)

# def y(z1,z2,b):


def classify_points():
    # Create a grid of points in the x1-x2 space
    x1 = np.linspace(-5, 5, 100)
    x2 = np.linspace(-5, 5, 100)
    X1, X2 = np.meshgrid(x1, x2)
    points = np.c_[X1.ravel(), X2.ravel()]

    # Classify each point
    classifications = []
    for x1, x2 in points:
        # Calculate z1 and z2
        z1 = relu(w11 * x1 + w21 * x2)
        z2 = relu(w12 * x1 + w22 * x2)
        
        # Calculate output y_hat
        y_hat = np.sign(z1 + z2 + b)
        classifications.append(1 if y_hat > 0 else 0)

    # Reshape classifications to match the grid shape
    classifications = np.array(classifications).reshape(X1.shape)

    # Plot the classification results
    plt.figure(figsize=(8, 8))
    plt.contourf(X1, X2, classifications, levels=[-0.5, 0.5, 1.5], colors=['red', 'blue'], alpha=0.3)
    plt.colorbar(ticks=[0, 1], label="Class")
    plt.xlabel(r'$x_1$')
    plt.ylabel(r'$x_2$')
    plt.title("Point Classification")

    # Define boundaries for z1 and z2
    x = np.linspace(-5, 5, 100)
    z1_boundary = (w11 / -w21) * x  # Boundary for z1: x2 = (1/2) * x1
    z2_boundary = (w12 / -w22) * x  # Boundary for z2: x2 = 3 * x1
    # overall_boundary = (-(w11 + w12) / (w21 + w22)) * x - b / (w21 + w22)  # Overall boundary

    
    # Overlay the decision boundaries
    plt.plot(x, z1_boundary, 'r--', label=r'Decision boundary for $z_1$')
    plt.plot(x, z2_boundary, 'b--', label=r'Decision boundary for $z_2$')
    x_coords = [1.32, -0.34, -0.17, 5]
    y_coords = [4.93, -0.34, -0.78, 2]

    # Draw each line segment by specifying consecutive points
    plt.plot([x_coords[0], x_coords[1]], [y_coords[0], y_coords[1]], color='black', linewidth=2)
    plt.plot([x_coords[1], x_coords[2]], [y_coords[1], y_coords[2]], color='black', linewidth=2)
    plt.plot([x_coords[2], x_coords[3]], [y_coords[2], y_coords[3]], color='black', linewidth=2)


    slope_intersection_x = (w12 * b - w11 * b) / (w11 * w22 - w12 * w21)
    slope_intersection_y = (w11 * slope_intersection_x) / -w21
    plt.plot(-0.34, -0.34, 'go', label='Boundary change point')
    plt.plot(-0.17, -0.78, 'go', label='Boundary change point')

    plt.legend(loc='upper left')
    plt.grid(True)
    plt.show()

# Run the classification function
classify_points()