# routes/seo_routes.py - SEO routes (sitemap, robots, schema.org)

from flask import Blueprint, render_template, make_response, url_for, request, send_from_directory
from datetime import datetime
from models import LearningPath, Subject, Module, Lesson

seo_bp = Blueprint('seo', __name__)

@seo_bp.route('/sitemap.xml', strict_slashes=False)
def sitemap():
    """Generate dynamic sitemap.xml"""
    
    pages = []
    
    # Static pages - High priority
    static_pages = [
        ('index', 1.0, 'daily'),
        ('big_info', 0.8, 'weekly'),
        ('contact', 0.5, 'monthly'),
        ('privacy', 0.3, 'yearly'),
        ('terms', 0.3, 'yearly'),
    ]
    
    for endpoint, priority, changefreq in static_pages:
        try:
            url = url_for(endpoint, _external=True)
            pages.append({
                'loc': url,
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'priority': priority,
                'changefreq': changefreq
            })
        except:
            pass
    
    # Learning paths - Medium priority
    try:
        learning_paths = LearningPath.query.all()
        for path in learning_paths:
            pages.append({
                'loc': url_for('learning.index', _external=True),
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'priority': 0.8,
                'changefreq': 'weekly'
            })
    except:
        pass
    
    # Subjects - Medium priority
    try:
        subjects = Subject.query.all()
        for subject in subjects:
            # Add subject URLs if you have subject detail pages
            pass
    except:
        pass
    
    # Modules - Lower priority
    try:
        modules = Module.query.all()
        for module in modules:
            # Add module URLs if you have module detail pages
            pass
    except:
        pass
    
    # Generate XML
    sitemap_xml = render_template('seo/sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    
    return response


@seo_bp.route('/robots.txt', strict_slashes=False)
def robots_txt():
    """Serve robots.txt"""
    import os
    from flask import current_app
    static_folder = current_app.static_folder
    return send_from_directory(static_folder, 'robots.txt', mimetype='text/plain')


@seo_bp.route('/schema.json', strict_slashes=False)
def schema_json():
    """Generate JSON-LD structured data for organization"""
    
    schema = {
        "@context": "https://schema.org",
        "@type": "EducationalOrganization",
        "name": "Mentora",
        "description": "Professional BIG exam preparation platform for healthcare workers in the Netherlands",
        "url": url_for('index', _external=True),
        "logo": url_for('static', filename='images/favicon.png', _external=True),
        "sameAs": [
            # Add social media links here when available
        ],
        "address": {
            "@type": "PostalAddress",
            "addressCountry": "NL"
        },
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Medical Education Courses",
            "itemListElement": [
                {
                    "@type": "Course",
                    "name": "BIG Exam Preparation",
                    "description": "Comprehensive preparation for healthcare professionals",
                    "provider": {
                        "@type": "Organization",
                        "name": "Mentora"
                    }
                }
            ]
        }
    }
    
    response = make_response(schema)
    response.headers['Content-Type'] = 'application/ld+json; charset=utf-8'
    
    return response


@seo_bp.route('/seo-debug')
def seo_debug():
    """Debug route to check SEO routes"""
    from flask import current_app, jsonify
    routes = []
    for rule in current_app.url_map.iter_rules():
        if 'seo' in rule.endpoint or 'robots' in str(rule) or 'sitemap' in str(rule):
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'path': str(rule)
            })
    return jsonify(routes)
