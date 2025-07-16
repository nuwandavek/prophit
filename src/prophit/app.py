from fasthtml.common import *
from .models.database import init_database
from .routes.market_routes import register_market_routes


def create_app():
    """Create and configure the FastHTML app"""
    
    # Initialize database
    init_database()
    
    # Create app with styling
    app, rt = fast_app(
        pico=True,
        hdrs=(
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap"),
            Script(src="https://unpkg.com/htmx.org@1.9.6"),
            Script(src="https://cdn.jsdelivr.net/npm/chart.js"),
            Style("""
                :root {
                    --primary: #c0392b;
                    --primary-hover: #e74c3c;
                    --secondary: #56d364;
                    --danger: #f85149;
                    --background: #1a1a1a;
                    --surface: #2a2a2a;
                    --surface-2: #333;
                    --text: #e0e0e0;
                    --text-light: #888;
                    --border: #444;
                    --border-light: #555;
                    --accent: #c0392b;
                    --success: #56d364;
                    --shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                    --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.4);
                }
                
                * {
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'JetBrains Mono', monospace;
                    background: var(--background);
                    min-height: 100vh;
                    margin: 0;
                    padding: 2rem 1rem;
                    color: var(--text);
                    line-height: 1.5;
                }
                
                .container {
                    max-width: 1000px;
                    margin: 0 auto;
                    background: var(--surface);
                    border-radius: 6px;
                    box-shadow: var(--shadow);
                    padding: 2rem;
                }
                
                h1 {
                    text-align: center;
                    color: var(--text);
                    margin-bottom: 2rem;
                    font-size: 2.5rem;
                    font-weight: 600;
                }
                
                h2 {
                    color: var(--text);
                    font-size: 1.5rem;
                    font-weight: 500;
                    margin-bottom: 1.5rem;
                }
                
                .market-card {
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: 6px;
                    padding: 20px;
                    margin: 20px 0;
                    box-shadow: var(--shadow);
                    transition: all 0.2s ease;
                }
                
                .market-card:hover {
                    transform: translateY(-2px);
                    box-shadow: var(--shadow-lg);
                    border-color: var(--primary);
                }
                
                .market-card h3 {
                    color: var(--text);
                    margin-bottom: 15px;
                    font-size: 1.2rem;
                    font-weight: 500;
                }
                
                .market-card h3 a {
                    color: var(--primary);
                    text-decoration: none;
                }
                
                .market-card h3 a:hover {
                    color: var(--primary-hover);
                    text-decoration: underline;
                }
                
                .prices-container {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 15px;
                }
                
                .price-display {
                    flex: 1;
                    background: var(--surface-2);
                    padding: 15px;
                    border-radius: 6px;
                    text-align: center;
                    font-size: 1.1rem;
                    font-weight: 600;
                    border: 1px solid var(--border);
                }
                
                .price-display.yes {
                    color: var(--secondary);
                    border-left: 3px solid var(--secondary);
                }
                
                .price-display.no {
                    color: var(--danger);
                    border-left: 3px solid var(--danger);
                }
                
                .volume-info {
                    display: flex;
                    justify-content: center;
                    margin-bottom: 15px;
                    font-size: 0.9rem;
                    color: var(--text-light);
                    font-weight: 500;
                }
                
                .trade-form {
                    display: flex;
                    gap: 15px;
                    align-items: center;
                    flex-wrap: wrap;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid var(--border);
                    justify-content: center;
                }
                
                .quantity-input {
                    width: 80px;
                }
                
                .buy-btn {
                    flex-shrink: 0;
                    width: auto !important;
                }
                
                .outcome-btn {
                    padding: 10px 20px;
                    border: 1px solid var(--border);
                    background: var(--surface-2);
                    color: var(--text);
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: 500;
                    font-family: 'JetBrains Mono', monospace;
                    transition: all 0.2s ease;
                }
                
                .outcome-btn:hover {
                    background: var(--border);
                    transform: translateY(-1px);
                }
                
                .outcome-btn.selected {
                    background: var(--primary);
                    color: white;
                    border-color: var(--primary);
                }
                
                .outcome-btn.yes.selected {
                    background: var(--secondary);
                    border-color: var(--secondary);
                }
                
                .outcome-btn.no.selected {
                    background: var(--danger);
                    border-color: var(--danger);
                }
                
                input[type="number"] {
                    padding: 10px;
                    border: 1px solid var(--border);
                    border-radius: 6px;
                    background: var(--surface-2);
                    color: var(--text);
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 1rem;
                    width: 100px;
                    transition: border-color 0.2s ease;
                }
                
                input[type="number"]:focus {
                    outline: none;
                    border-color: var(--primary);
                    background: var(--surface);
                }
                
                input[type="text"] {
                    padding: 10px;
                    border: 1px solid var(--border);
                    border-radius: 6px;
                    background: var(--surface-2);
                    color: var(--text);
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 1rem;
                    transition: border-color 0.2s ease;
                }
                
                input[type="text"]:focus {
                    outline: none;
                    border-color: var(--primary);
                    background: var(--surface);
                }
                
                button[type="submit"] {
                    background: var(--primary);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: 500;
                    font-family: 'JetBrains Mono', monospace;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                
                button[type="submit"]:hover {
                    background: var(--primary-hover);
                    transform: translateY(-1px);
                }
                
                .create-market-form {
                    background: var(--surface-2);
                    padding: 20px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                    border: 1px solid var(--border);
                }
                
                .create-market-form h2 {
                    color: var(--text);
                    margin-bottom: 15px;
                    font-size: 1.3rem;
                    font-weight: 500;
                }
                
                .markets-section h2 {
                    color: var(--text);
                    margin-bottom: 20px;
                    font-size: 1.3rem;
                    font-weight: 500;
                }
                
                .markets-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }
                
                .market-item {
                    width: 100%;
                }
                
                #market-search {
                    transition: border-color 0.2s ease;
                }
                
                #market-search:focus {
                    outline: none;
                    border-color: var(--primary);
                }
                
                .empty-state {
                    text-align: center;
                    padding: 40px;
                    color: var(--text-light);
                    font-size: 1rem;
                    background: var(--surface-2);
                    border-radius: 6px;
                    border: 1px solid var(--border);
                }
                
                .chart-container {
                    background: var(--surface-2);
                    padding: 20px;
                    border-radius: 6px;
                    border: 1px solid var(--border);
                    box-shadow: var(--shadow);
                    height: 250px;
                    width: 100%;
                    position: relative;
                }
                
                .back-link {
                    display: inline-block;
                    margin-bottom: 20px;
                    color: var(--primary);
                    text-decoration: none;
                    font-weight: 500;
                }
                
                .back-link:hover {
                    color: var(--primary-hover);
                    text-decoration: underline;
                }
                
                @media (max-width: 640px) {
                    .prices-container {
                        flex-direction: column;
                        gap: 1rem;
                    }
                    
                    .volume-info {
                        margin-bottom: 10px;
                    }
                    
                    .trade-form {
                        flex-direction: column;
                        align-items: stretch;
                    }
                    
                    .outcome-btn {
                        justify-content: center;
                    }
                    
                    .quantity-input {
                        width: 100%;
                    }
                    
                    .buy-btn {
                        width: auto;
                    }
                    
                    .markets-grid {
                        grid-template-columns: 1fr;
                        gap: 15px;
                    }
                }
            """)
        )
    )
    
    # Register routes
    register_market_routes(app, rt)
    
    return app, rt