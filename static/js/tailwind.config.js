theme: {
    extend: {
      animation: {
        'float-slow': 'float 15s ease-in-out infinite',
        'float-medium': 'float 8s ease-in-out infinite',
        'float-fast': 'float 6s ease-in-out infinite',
        'fade-in': 'fadeIn 0.8s ease-out forwards',
        'slide-up': 'slideUp 0.8s ease-out forwards',
        'slide-in-right': 'slideInRight 0.8s ease-out forwards',
        'scale-in': 'scaleIn 0.5s ease-out forwards',
        'grid': 'gridMovement 20s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
          '50%': { transform: 'translateY(-20px) rotate(2deg)' },
        },
        fadeIn: {
          to: { opacity: '1' },
        },
        slideUp: {
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          to: { opacity: '1', transform: 'scale(1)' },
        },
        gridMovement: {
          '0%': { backgroundPosition: '0 0' },
          '100%': { backgroundPosition: '50px 50px' },
        },
      },
      backgroundImage: {
        'grid-pattern': `linear-gradient(to right, rgba(13, 148, 136, 0.05) 1px, transparent 1px),
                         linear-gradient(to bottom, rgba(13, 148, 136, 0.05) 1px, transparent 1px)`,
      },
    },
  }
  