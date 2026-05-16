import kagglehub

# Download latest version
path = kagglehub.dataset_download("devvraj/chennai-restaurant-dataset")

print("Path to dataset files:", path)
