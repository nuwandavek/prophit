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
            Script(src="https://unpkg.com/htmx.org@1.9.6"),
            Style("""
                :root {
                    --primary: #6366f1;
                    --primary-light: #8b5cf6;
                    --secondary: #10b981;
                    --danger: #ef4444;
                    --surface: #ffffff;
                    --surface-2: #f8fafc;
                    --surface-3: #f1f5f9;
                    --text: #1e293b;
                    --text-light: #64748b;
                    --border: #e2e8f0;
                    --border-light: #f1f5f9;
                    --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
                    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
                }
                
                * {
                    box-sizing: border-box;
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    margin: 0;
                    padding: 2rem 1rem;
                    color: var(--text);
                }
                
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: var(--surface);
                    border-radius: 16px;
                    box-shadow: var(--shadow-lg);
                    padding: 2rem;
                }
                
                h1 {
                    text-align: center;
                    color: var(--primary);
                    margin-bottom: 2rem;
                    font-size: 2.5rem;
                    font-weight: 700;
                    background: linear-gradient(135deg, var(--primary), var(--primary-light));
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }
                
                .market-card {
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 1.5rem 0;
                    box-shadow: var(--shadow);
                    transition: all 0.2s ease;
                    position: relative;
                    overflow: hidden;
                }
                
                .market-card:hover {
                    transform: translateY(-2px);
                    box-shadow: var(--shadow-lg);
                    border-color: var(--primary);
                }
                
                .market-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: linear-gradient(90deg, var(--primary), var(--primary-light));
                }
                
                .market-card h3 {
                    color: var(--text);
                    margin-bottom: 1rem;
                    font-size: 1.25rem;
                    font-weight: 600;
                }
                
                .prices-container {
                    display: flex;
                    gap: 2rem;
                    margin-bottom: 1rem;
                }
                
                .price-display {
                    flex: 1;
                    background: var(--surface-2);
                    padding: 1rem;
                    border-radius: 8px;
                    text-align: center;
                    font-size: 1.1rem;
                    font-weight: 600;
                    transition: all 0.2s ease;
                }
                
                .price-display.yes {
                    color: var(--secondary);
                    border-left: 4px solid var(--secondary);
                }
                
                .price-display.no {
                    color: var(--danger);
                    border-left: 4px solid var(--danger);
                }
                
                .shares-info {
                    display: flex;
                    gap: 2rem;
                    margin-bottom: 1rem;
                    font-size: 0.875rem;
                    color: var(--text-light);
                }
                
                .trade-form {
                    display: flex;
                    gap: 1rem;
                    align-items: center;
                    flex-wrap: wrap;
                    margin-top: 1.5rem;
                    padding-top: 1.5rem;
                    border-top: 1px solid var(--border-light);
                }
                
                .outcome-btn {
                    padding: 0.75rem 1.5rem;
                    border: 2px solid var(--border);
                    background: var(--surface);
                    color: var(--text);
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: all 0.2s ease;
                    border: none;
                    box-shadow: var(--shadow);
                }
                
                .outcome-btn:hover {
                    transform: translateY(-1px);
                    box-shadow: var(--shadow-lg);
                }
                
                .outcome-btn.selected {
                    background: var(--primary);
                    color: white;
                    transform: translateY(-1px);
                    box-shadow: var(--shadow-lg);
                }
                
                .outcome-btn.yes.selected {
                    background: var(--secondary);
                }
                
                .outcome-btn.no.selected {
                    background: var(--danger);
                }
                
                input[type="number"] {
                    padding: 0.75rem;
                    border: 2px solid var(--border);
                    border-radius: 8px;
                    font-size: 1rem;
                    width: 120px;
                    transition: border-color 0.2s ease;
                }
                
                input[type="number"]:focus {
                    outline: none;
                    border-color: var(--primary);
                }
                
                input[type="text"] {
                    padding: 0.75rem;
                    border: 2px solid var(--border);
                    border-radius: 8px;
                    font-size: 1rem;
                    transition: border-color 0.2s ease;
                }
                
                input[type="text"]:focus {
                    outline: none;
                    border-color: var(--primary);
                }
                
                button[type="submit"] {
                    background: var(--primary);
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    border-radius: 8px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    box-shadow: var(--shadow);
                }
                
                button[type="submit"]:hover {
                    background: var(--primary-light);
                    transform: translateY(-1px);
                    box-shadow: var(--shadow-lg);
                }
                
                .create-market-form {
                    background: var(--surface-2);
                    padding: 2rem;
                    border-radius: 12px;
                    margin-bottom: 2rem;
                    border: 1px solid var(--border-light);
                }
                
                .create-market-form h2 {
                    color: var(--text);
                    margin-bottom: 1.5rem;
                    font-size: 1.5rem;
                    font-weight: 600;
                }
                
                .markets-section h2 {
                    color: var(--text);
                    margin-bottom: 1.5rem;
                    font-size: 1.5rem;
                    font-weight: 600;
                }
                
                .empty-state {
                    text-align: center;
                    padding: 3rem;
                    color: var(--text-light);
                    font-size: 1.1rem;
                }
                
                @media (max-width: 640px) {
                    .prices-container {
                        flex-direction: column;
                        gap: 1rem;
                    }
                    
                    .shares-info {
                        flex-direction: column;
                        gap: 0.5rem;
                    }
                    
                    .trade-form {
                        flex-direction: column;
                        align-items: stretch;
                    }
                    
                    .outcome-btn {
                        justify-content: center;
                    }
                }
            """)
        )
    )
    
    # Register routes
    register_market_routes(app, rt)
    
    return app, rt