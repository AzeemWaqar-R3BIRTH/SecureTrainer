/**
 * Cyber Matrix Hero Animation
 * Creates an interactive grid of characters that respond to mouse movement
 */

class CyberMatrix {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with id "${containerId}" not found`);
            return;
        }

        this.chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789<>/?;:"[]{}\\|!@#$%^&*()_+-=';
        this.columns = 0;
        this.rows = 0;
        this.tiles = [];
        
        this.init();
    }

    init() {
        this.createGrid();
        this.attachEventListeners();
        this.startAnimation();
    }

    createTile(index) {
        const tile = document.createElement('div');
        tile.classList.add('matrix-tile');
        tile.textContent = this.chars[Math.floor(Math.random() * this.chars.length)];
        
        tile.addEventListener('click', (e) => {
            const target = e.target;
            target.textContent = this.chars[Math.floor(Math.random() * this.chars.length)];
            target.classList.add('matrix-glitch');
            setTimeout(() => target.classList.remove('matrix-glitch'), 200);
        });

        return tile;
    }

    createGrid() {
        this.container.innerHTML = '';
        
        const size = 60;
        this.columns = Math.floor(window.innerWidth / size);
        this.rows = Math.floor(window.innerHeight / size);
        
        this.container.style.setProperty('--columns', this.columns);
        this.container.style.setProperty('--rows', this.rows);
        
        const totalTiles = this.columns * this.rows;
        this.tiles = [];
        
        for (let i = 0; i < totalTiles; i++) {
            const tile = this.createTile(i);
            this.container.appendChild(tile);
            this.tiles.push(tile);
        }
    }

    handleMouseMove(e) {
        const mouseX = e.clientX;
        const mouseY = e.clientY;
        const radius = window.innerWidth / 4;

        this.tiles.forEach(tile => {
            const rect = tile.getBoundingClientRect();
            const tileX = rect.left + rect.width / 2;
            const tileY = rect.top + rect.height / 2;

            const distance = Math.sqrt(
                Math.pow(mouseX - tileX, 2) + Math.pow(mouseY - tileY, 2)
            );

            const intensity = Math.max(0, 1 - distance / radius);
            tile.style.setProperty('--intensity', intensity);
        });
    }

    handleResize() {
        this.createGrid();
    }

    attachEventListeners() {
        this.boundMouseMove = this.handleMouseMove.bind(this);
        this.boundResize = this.handleResize.bind(this);
        
        window.addEventListener('mousemove', this.boundMouseMove);
        window.addEventListener('resize', this.boundResize);
    }

    startAnimation() {
        // Random character changes
        setInterval(() => {
            const randomTiles = [];
            for (let i = 0; i < 5; i++) {
                const randomIndex = Math.floor(Math.random() * this.tiles.length);
                randomTiles.push(this.tiles[randomIndex]);
            }
            
            randomTiles.forEach(tile => {
                if (tile) {
                    tile.textContent = this.chars[Math.floor(Math.random() * this.chars.length)];
                }
            });
        }, 200);
    }

    destroy() {
        window.removeEventListener('mousemove', this.boundMouseMove);
        window.removeEventListener('resize', this.boundResize);
    }
}

// Fade-in animation for hero content
function initHeroAnimations() {
    const heroElements = document.querySelectorAll('.hero-fade-in');
    
    heroElements.forEach((element, index) => {
        setTimeout(() => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                element.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 100);
        }, index * 200 + 500);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const matrixContainer = document.getElementById('cyber-matrix-grid');
    if (matrixContainer) {
        const matrix = new CyberMatrix('cyber-matrix-grid');
        initHeroAnimations();
    }
});
