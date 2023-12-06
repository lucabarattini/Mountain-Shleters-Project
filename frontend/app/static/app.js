document.addEventListener('DOMContentLoaded', (event) => {
    // This code runs when the document is ready

    // Initialize all carousel components
    var carousels = document.querySelectorAll('.carousel');
    carousels.forEach((carousel) => {
        new bootstrap.Carousel(carousel, {
            // Options can be passed here if needed
            interval: 2000, // Example: Change slide every 2 seconds
            wrap: true      // Allows the carousel to cycle continuously
        });
    });

    // Additional JavaScript for other components can be added here
});