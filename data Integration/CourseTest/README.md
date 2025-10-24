# Personal Portfolio

This project is a personal portfolio webpage that showcases an individual's skills and provides a contact form. The webpage is designed to be responsive, allowing it to adapt to different devices. It includes features such as dynamic theme switching, skill display animations, and form validation.

## Project Structure

```
personal-portfolio
├── src
│   ├── index.html          # Main HTML file for the portfolio
│   ├── css
│   │   └── styles.css      # CSS styles for responsive design and theme switching
│   └── js
│       ├── main.js         # Main JavaScript for smooth scrolling and animations
│       ├── theme.js        # JavaScript for dynamic theme switching
│       └── form-validation.js # JavaScript for contact form validation
├── nginx
│   └── personal-portfolio.conf # Nginx configuration file for serving the portfolio
├── .gitignore              # Files and directories to ignore in version control
└── README.md               # Project documentation
```

## Features

- **Responsive Design**: The webpage is designed to work on various screen sizes, ensuring a good user experience on both mobile and desktop devices.
- **Dynamic Theme Switching**: Users can switch between different themes to customize their viewing experience.
- **Skill Display Animation**: Skills are presented with animations to enhance visual appeal.
- **Contact Form Validation**: The contact form includes validation to ensure that user inputs are correct before submission.
- **Smooth Scrolling Navigation**: Navigation links provide a smooth scrolling effect for a better user experience.

## Installation and Configuration

1. Clone the repository:
   ```
   git clone <repository-url>
   cd personal-portfolio
   ```

2. Install and configure Nginx on your operating system. Ensure that you have the necessary permissions to modify configuration files.

3. Copy the `nginx/personal-portfolio.conf` file to your Nginx configuration directory (usually `/etc/nginx/sites-available/` on Linux).

4. Create a symbolic link to the configuration file in the `sites-enabled` directory:
   ```
   sudo ln -s /etc/nginx/sites-available/personal-portfolio.conf /etc/nginx/sites-enabled/
   ```

5. Test the Nginx configuration:
   ```
   sudo nginx -t
   ```

6. Restart Nginx to apply the changes:
   ```
   sudo systemctl restart nginx
   ```

## Accessing the Webpage

Once Nginx is configured and running, you can access the personal portfolio webpage by navigating to `http://localhost` in your web browser. The webpage will display your personal introduction and allow users to interact with the features provided.

## Screenshots

Include screenshots of the webpage to showcase its design and functionality.