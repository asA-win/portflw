document.addEventListener('DOMContentLoaded', function() {

    // --- MOBILE MENU TOGGLE ---
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            hamburger.classList.toggle('is-active');
            document.body.classList.toggle('menu-open');
        });

        // Close menu when a link is clicked
        document.querySelectorAll('.nav-menu a').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                hamburger.classList.remove('is-active');
                document.body.classList.remove('menu-open');
            });
        });
    }

    // --- BACK TO TOP ---
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        });

        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // --- STICKY NAVBAR & SHRINK ON SCROLL ---
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
        let lastScrollTop = 0;
        window.addEventListener('scroll', () => {
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

            if (scrollTop > lastScrollTop) {
                // Scroll Down
                navbar.style.top = `-${navbar.offsetHeight}px`;
            } else {
                // Scroll Up
                navbar.style.top = '0';
            }
            lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; // For Mobile or negative scrolling

            // Add scrolled class for styling (e.g., shrink)
            if (scrollTop > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // --- SCROLL REVEAL ANIMATIONS ---
    const revealElements = document.querySelectorAll('.reveal');

    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        revealElements.forEach(el => {
            const elementTop = el.getBoundingClientRect().top;
            if (elementTop < windowHeight - 100) { // 100px before it's in view
                el.classList.add('active');
            }
        });
    };

    window.addEventListener('scroll', revealOnScroll);
    revealOnScroll(); // Initial check

    // --- TESTIMONIAL SLIDER ---
    const testimonialContainer = document.querySelector('.testimonial-carousel-container');
    if (testimonialContainer) {
        const testimonials = testimonialContainer.querySelectorAll('.testimonial');
        const nextBtn = testimonialContainer.querySelector('.next');
        const prevBtn = testimonialContainer.querySelector('.prev');
        const dotsContainer = testimonialContainer.querySelector('.testimonial-dots');
        let currentTestimonial = 0;
        let testimonialInterval;

        // Create Dots
        testimonials.forEach((_, i) => {
            const dot = document.createElement('div');
            dot.classList.add('dot');
            if (i === 0) dot.classList.add('active');
            dot.addEventListener('click', () => {
                stopSlider();
                currentTestimonial = i;
                showTestimonial(currentTestimonial);
                startSlider();
            });
            dotsContainer.appendChild(dot);
        });

        const showTestimonial = (index) => {
            testimonials.forEach((testimonial, i) => {
                testimonial.classList.remove('active', 'fade-in');
                if (i === index) {
                    testimonial.classList.add('active', 'fade-in');
                }
            });
            // Update Dots
            const dots = dotsContainer.querySelectorAll('.dot');
            dots.forEach((dot, i) => {
                dot.classList.remove('active');
                if (i === index) dot.classList.add('active');
            });
        };

        const nextTestimonial = () => {
            currentTestimonial = (currentTestimonial + 1) % testimonials.length;
            showTestimonial(currentTestimonial);
        };

        const prevTestimonial = () => {
            currentTestimonial = (currentTestimonial - 1 + testimonials.length) % testimonials.length;
            showTestimonial(currentTestimonial);
        };

        const startSlider = () => {
            testimonialInterval = setInterval(nextTestimonial, 5000); // Change every 5 seconds
        };

        const stopSlider = () => {
            clearInterval(testimonialInterval);
        };

        if (testimonials.length > 1) {
            nextBtn.addEventListener('click', () => {
                stopSlider();
                nextTestimonial();
                startSlider();
            });

            prevBtn.addEventListener('click', () => {
                stopSlider();
                prevTestimonial();
                startSlider();
            });
            
            testimonialContainer.addEventListener('mouseenter', stopSlider);
            testimonialContainer.addEventListener('mouseleave', startSlider);

            showTestimonial(currentTestimonial);
            startSlider();
        }
    }

    // --- PORTFOLIO FILTERING ---
    const filterButtons = document.querySelectorAll('.portfolio-filter button');
    const portfolioItems = document.querySelectorAll('.portfolio-item');

    if (filterButtons.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Set active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                const filter = button.getAttribute('data-filter');

                portfolioItems.forEach(item => {
                    item.style.display = 'none';
                    if (item.classList.contains(filter) || filter === '*') {
                        item.style.display = 'block';
                        item.classList.add('fade-in');
                    }
                });
            });
        });
    }

    // --- FORM VALIDATION ---
    const contactForm = document.querySelector('#contact-form');

    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            let isValid = true;
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const phone = document.getElementById('phone');
            const message = document.getElementById('message');

            // Simple validation: check if fields are not empty
            if (name.value.trim() === '') {
                isValid = false;
                alert('Please enter your name.');
                name.focus();
                return;
            }

            if (email.value.trim() === '' || !validateEmail(email.value.trim())) {
                isValid = false;
                alert('Please enter a valid email address.');
                email.focus();
                return;
            }

            if (message.value.trim() === '') {
                isValid = false;
                alert('Please enter your message.');
                message.focus();
                return;
            }

            if (isValid) {
                // Prepare form data
                const formData = {
                    name: name.value,
                    email: email.value,
                    phone: phone.value,
                    service: document.getElementById('service').value,
                    message: message.value
                };

                // Send data to backend
                fetch('https://portflw.onrender.com/api/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                })
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        // Throw error with the detail from backend if it exists
                        throw new Error(data.detail || 'Network response was not ok');
                    }
                    return data;
                })
                .then(data => {
                    alert(data.message || 'Thank you for your message! We will get back to you soon.');
                    contactForm.reset();
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error: ' + error.message);
                });
            }
        });
    }
    
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }
});
