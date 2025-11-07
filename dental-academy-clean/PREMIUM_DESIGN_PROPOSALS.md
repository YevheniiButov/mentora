<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium Tab - Mentora</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f8f9fa;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* ============================================================
           PREMIUM SECTION
           ============================================================ */

        .premium-section {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }

        /* Hero Area */
        .premium-hero {
            padding: 60px 40px;
            text-align: center;
            background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
            position: relative;
            overflow: hidden;
        }

        /* Decorative elements */
        .premium-hero::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(245, 158, 11, 0.05), transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }

        .premium-hero::after {
            content: '';
            position: absolute;
            bottom: -50%;
            left: -50%;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(0, 102, 204, 0.03), transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }

        .premium-hero-content {
            position: relative;
            z-index: 1;
        }

        .premium-header-line {
            height: 4px;
            width: 60px;
            background: linear-gradient(90deg, #f59e0b, #fbbf24);
            margin: 0 auto 24px;
            border-radius: 2px;
            animation: lineExpand 0.8s ease-out;
        }

        @keyframes lineExpand {
            from {
                width: 0;
            }
            to {
                width: 60px;
            }
        }

        .premium-hero h1 {
            font-size: 42px;
            font-weight: 700;
            color: #1a1a2e;
            margin: 16px 0;
            letter-spacing: -0.5px;
        }

        .premium-star {
            color: #f59e0b;
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% {
                transform: translateY(0);
            }
            50% {
                transform: translateY(-8px);
            }
        }

        .premium-subtitle {
            font-size: 18px;
            color: #666;
            margin: 20px 0;
            line-height: 1.6;
        }

        .premium-features-list {
            display: flex;
            justify-content: center;
            gap: 32px;
            margin-top: 32px;
            flex-wrap: wrap;
        }

        .feature-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #666;
        }

        .feature-item i {
            color: #f59e0b;
            font-size: 18px;
        }

        /* Grid of Premium Cards */
        .premium-content {
            padding: 60px 40px;
        }

        .premium-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 32px;
            margin-bottom: 40px;
        }

        .premium-card {
            padding: 32px 24px;
            border: 2px solid #e0e7ff;
            border-radius: 12px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
            background: white;
        }

        /* Hover shine effect */
        .premium-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.1), transparent);
            transition: left 0.6s ease;
        }

        .premium-card:hover::before {
            left: 100%;
        }

        .premium-card:hover {
            border-color: #f59e0b;
            transform: translateY(-8px);
            box-shadow: 0 24px 48px rgba(245, 158, 11, 0.15);
        }

        .premium-card.popular {
            border-color: #f59e0b;
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.02), rgba(251, 191, 36, 0.02));
            transform: scale(1.05);
        }

        .premium-card.popular .popular-badge {
            display: inline-block;
            background: linear-gradient(135deg, #f59e0b, #fbbf24);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 16px;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% {
                box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7);
            }
            50% {
                box-shadow: 0 0 0 8px rgba(245, 158, 11, 0);
            }
        }

        .premium-icon {
            font-size: 48px;
            margin-bottom: 20px;
            animation: iconFloat 2s ease-in-out infinite;
            color: #f59e0b;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .premium-icon i {
            font-size: 48px;
            color: #f59e0b;
        }

        .premium-card:nth-child(1) .premium-icon {
            animation-delay: 0s;
        }

        .premium-card:nth-child(2) .premium-icon {
            animation-delay: 0.2s;
        }

        .premium-card:nth-child(3) .premium-icon {
            animation-delay: 0.4s;
        }

        @keyframes iconFloat {
            0%, 100% {
                transform: translateY(0);
            }
            50% {
                transform: translateY(-12px);
            }
        }

        .premium-card h3 {
            font-size: 20px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 12px;
        }

        .premium-card p {
            font-size: 14px;
            color: #666;
            line-height: 1.6;
            margin-bottom: 8px;
        }

        .premium-details {
            font-size: 13px;
            color: #999;
            margin: 20px 0;
            padding: 16px 0;
            border-top: 1px solid #e0e7ff;
            border-bottom: 1px solid #e0e7ff;
        }

        .premium-details ul {
            list-style: none;
            text-align: left;
        }

        .premium-details li {
            padding: 6px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .premium-details i {
            color: #f59e0b;
            font-size: 14px;
        }

        .btn-unlock {
            margin-top: 20px;
            padding: 12px 32px;
            background: white;
            color: #f59e0b;
            border: 2px solid #f59e0b;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .btn-unlock::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: #f59e0b;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.3s, height 0.3s;
            z-index: -1;
        }

        .btn-unlock:hover::before {
            width: 300px;
            height: 300px;
        }

        .btn-unlock:hover {
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(245, 158, 11, 0.3);
        }

        /* Bottom CTA */
        .premium-cta {
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
            border-top: 2px solid #e0e7ff;
        }

        .premium-cta h2 {
            font-size: 24px;
            color: #1a1a2e;
            margin-bottom: 12px;
        }

        .premium-cta p {
            font-size: 16px;
            color: #666;
            margin-bottom: 24px;
        }

        .btn-primary-cta {
            padding: 14px 40px;
            background: linear-gradient(135deg, #f59e0b, #fbbf24);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 24px rgba(245, 158, 11, 0.3);
        }

        .btn-primary-cta:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 32px rgba(245, 158, 11, 0.4);
        }

        /* Responsive */
        @media (max-width: 768px) {
            .premium-hero {
                padding: 40px 20px;
            }

            .premium-hero h1 {
                font-size: 28px;
            }

            .premium-content {
                padding: 40px 20px;
            }

            .premium-grid {
                gap: 20px;
            }

            .premium-card.popular {
                transform: scale(1);
            }

            .premium-features-list {
                flex-direction: column;
                gap: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="premium-section">
            <!-- HERO SECTION -->
            <div class="premium-hero">
                <div class="premium-hero-content">
                    <div class="premium-header-line"></div>
                    <h1><i class="bi bi-star-fill" style="color: #f59e0b; margin: 0 8px;"></i> Premium Access <i class="bi bi-star-fill" style="color: #f59e0b; margin: 0 8px;"></i></h1>
                    <p class="premium-subtitle">
                        Unlimited access to all learning materials<br>
                        Master every topic before your BIG exam
                    </p>
                    
                    <div class="premium-features-list">
                        <div class="feature-item">
                            <i class="bi bi-infinity"></i>
                            <span>Unlimited access</span>
                        </div>
                        <div class="feature-item">
                            <i class="bi bi-lightning-fill"></i>
                            <span>Learn faster</span>
                        </div>
                        <div class="feature-item">
                            <i class="bi bi-award"></i>
                            <span>Premium support</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- PREMIUM CARDS -->
            <div class="premium-content">
                <div class="premium-grid">
                    <!-- Card 1: Tests -->
                    <div class="premium-card">
                        <div class="premium-icon"><i class="bi bi-pencil-square"></i></div>
                        <h3>Unlimited Tests</h3>
                        <p>Practice with all exam questions</p>
                        <div class="premium-details">
                            <ul>
                                <li><i class="bi bi-check-circle-fill"></i> 500+ questions</li>
                                <li><i class="bi bi-check-circle-fill"></i> All categories</li>
                                <li><i class="bi bi-check-circle-fill"></i> Detailed feedback</li>
                            </ul>
                        </div>
                        <button class="btn-unlock">Unlock Now</button>
                    </div>

                    <!-- Card 2: Terms (POPULAR) -->
                    <div class="premium-card popular">
                        <div class="popular-badge"><i class="bi bi-star-fill"></i> Most Popular</div>
                        <div class="premium-icon"><i class="bi bi-book-half"></i></div>
                        <h3>All Medical Terms</h3>
                        <p>250+ medical terminology mastery</p>
                        <div class="premium-details">
                            <ul>
                                <li><i class="bi bi-check-circle-fill"></i> Full glossary</li>
                                <li><i class="bi bi-check-circle-fill"></i> 8 languages</li>
                                <li><i class="bi bi-check-circle-fill"></i> Pronunciation</li>
                            </ul>
                        </div>
                        <button class="btn-unlock">Unlock Now</button>
                    </div>

                    <!-- Card 3: English -->
                    <div class="premium-card">
                        <div class="premium-icon"><i class="bi bi-globe"></i></div>
                        <h3>English Content</h3>
                        <p>Learn in your preferred language</p>
                        <div class="premium-details">
                            <ul>
                                <li><i class="bi bi-check-circle-fill"></i> Full lessons</li>
                                <li><i class="bi bi-check-circle-fill"></i> Video guides</li>
                                <li><i class="bi bi-check-circle-fill"></i> Expert tips</li>
                            </ul>
                        </div>
                        <button class="btn-unlock">Unlock Now</button>
                    </div>
                </div>
            </div>

            <!-- CTA SECTION -->
            <div class="premium-cta">
                <h2>Ready to Master Your BIG Exam?</h2>
                <p>Thousands of healthcare professionals already trust Mentora</p>
                <button class="btn-primary-cta">
                    <i class="bi bi-lightning-charge"></i> Get Premium Access Now
                </button>
            </div>
        </div>
    </div>
</body>
