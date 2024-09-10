# Use the official Odoo 15 image as the base image
FROM odoo:15

# Switch to root user to install additional libraries
USER root

# Install the astor library
RUN pip install astor

# Switch back to the odoo user
USER odoo
