"""
CyberInspect Fingerprint Database

Structure:

category
    technology
        headers
        html
        cookies
        scripts
        meta
"""

FINGERPRINTS = {

    # -------------------------------------------------
    # WEB SERVERS
    # -------------------------------------------------

    "server": {

   "Vercel": {
    "headers": {
        "server": ["vercel"],
        "x-vercel-id": [""]
    },
    "html": [
        "vercel.app",
        "vercel.live"
    ]
},
        "NGINX": {
            "headers": {
                "server": ["nginx"]
            }
        },

        "Apache": {
            "headers": {
                "server": ["apache"]
            }
        },

        "Microsoft IIS": {
            "headers": {
                "server": ["microsoft-iis"]
            }
        },

        "LiteSpeed": {
            "headers": {
                "server": ["litespeed"]
            }
        },

        "OpenResty": {
            "headers": {
                "server": ["openresty"]
            }
        },

        "Caddy": {
            "headers": {
                "server": ["caddy"]
            }
        },

        "Gunicorn": {
            "headers": {
                "server": ["gunicorn"]
            }
        },

        "Uvicorn": {
            "headers": {
                "server": ["uvicorn"]
            }
        },

        "Cloudflare": {
    "headers": {
        "cf-ray": [""],
        "cf-cache-status": [""],
        "server": ["cloudflare"]
    }
},

    },

    # -------------------------------------------------
    # CMS
    # -------------------------------------------------

    "cms": {

        "WordPress": {
            "html": [
                "wp-content",
                "wp-includes",
                "wp-json"
            ],
            "cookies": [
                "wordpress_",
                "wp-settings"
            ]
        },

        "Drupal": {
            "html": [
                "drupal",
                "/sites/default/"
            ]
        },

        "Joomla": {
            "html": [
                "joomla",
                "/media/system/"
            ]
        },

        "Shopify": {
            "html": [
                "cdn.shopify.com",
                "shopify-payment-button",
                "Shopify.theme"
            ]
        },

        "Squarespace": {
            "html": [
                "static1.squarespace.com",
                "Squarespace.Analytics"
            ]
        },

        "Webflow": {
            "html": [
                "webflow.js",
                "w-webflow"
            ]
        },

        "Ghost": {
            "html": [
                "ghost-content",
                "ghost-sdk"
            ]
        },

        "Wix": {
            "html": [
                "wixstatic",
                "wix-image"
            ]
        }

    },

    # -------------------------------------------------
    # FRONTEND FRAMEWORKS
    # -------------------------------------------------

    "frontend": {

        "React": {
            "html": [
                "__REACT_DEVTOOLS_GLOBAL_HOOK__",
                "data-reactroot"
            ]
        },
"Next.js": {
    "confidence": 100,
    "html": [
        "__NEXT_DATA__",
        "/_next/"
    ],
    "scripts": [
        "_next/static"
    ],
    "meta": [
        "next-head-count"
    ],
    "headers": {},
    "cookies": []
},

        "Vue.js": {
            "html": [
                "__VUE__",
                "data-v-"
            ]
        },

        "Nuxt.js": {
            "html": [
                "__NUXT__"
            ]
        },

        "Angular": {
            "html": [
                "ng-version",
                "ng-app"
            ]
        },

        "Svelte": {
            "html": [
                "__SVELTE__"
            ]
        }
        ,
        "Bootstrap": {
    "html": [
        "bootstrap.min.css",
        "bootstrap.bundle.min.js"
    ]
},
"Tailwind CSS": {
    "html": [
        "tailwindcss",
        "tailwind.min.css",
        "__next_css__"
    ]
},
"jQuery": {
    "scripts": [
        "jquery.min.js",
        "jquery.js"
    ]
},
"Google Analytics": {
    "scripts": [
        "googletagmanager",
        "google-analytics",
        "gtag/js"
    ]
},


    },

    # -------------------------------------------------
    # BACKEND FRAMEWORKS
    # -------------------------------------------------

    "backend": {

        "Express": {
            "headers": {
                "x-powered-by": [
                    "Express"
                ]
            }
        },

        "ASP.NET": {
            "headers": {
                "x-powered-by": [
                    "ASP.NET"
                ]
            },
            "cookies": [
                "ASP.NET_SessionId"
            ]
        },

        "Laravel": {
            "cookies": [
                "laravel_session",
                "XSRF-TOKEN"
            ]
        },

        "Django": {
            "cookies": [
                "csrftoken",
                "sessionid"
            ]
        },

        "Flask": {
            "headers": {
                "server": [
                    "Werkzeug"
                ]
            }
        }

    },

    # -------------------------------------------------
    # CDN
    # -------------------------------------------------

    "cdn": {
 
         "Vercel": {
           "headers": {
             "server": ["vercel"]
           },
    "html": [
        "vercel"
    ]
},
        "Cloudflare": {
            "headers": {
                "cf-ray": [""]
            }
        },

        "Fastly": {
            "headers": {
                "x-served-by": [
                    "cache-"
                ]
            }
        },

        "Amazon CloudFront": {
            "headers": {
                "x-cache": [
                    "CloudFront"
                ]
            }
        },

        "Akamai": {
            "headers": {
                "server": [
                    "Akamai"
                ]
            }
        }

    }

}