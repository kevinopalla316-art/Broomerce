document.addEventListener('DOMContentLoaded', function () {
  const productNavLinks = {
    shop: Array.from(document.querySelectorAll('.shop-link')),
    products: Array.from(document.querySelectorAll('.products-link'))
  };

  const syncProductSectionNav = () => {
    const path = window.location.pathname;
    const hash = (window.location.hash || '').replace('#', '');
    const isProductsRoute = path === '/products' || path === '/products/';
    const isShopTarget = !hash || hash === 'shop';
    const isProductsTarget = hash === 'products-list';

    productNavLinks.shop.forEach((link) => {
      link.classList.toggle('active', isProductsRoute && isShopTarget);
    });

    productNavLinks.products.forEach((link) => {
      link.classList.toggle('active', isProductsRoute && isProductsTarget);
    });
  };

  syncProductSectionNav();
  window.addEventListener('hashchange', syncProductSectionNav);

  const flashMessages = document.querySelectorAll('.flash');
  flashMessages.forEach((message) => {
    setTimeout(() => {
      message.style.opacity = '0';
      message.style.transition = 'opacity 0.3s ease';
      setTimeout(() => message.remove(), 300);
    }, 5000);
  });

  document.querySelectorAll('.qty-button').forEach((button) => {
    button.addEventListener('click', function () {
      const targetId = this.dataset.target || 'quantity';
      const input = document.getElementById(targetId);
      if (!input) {
        return;
      }

      const minValue = Number(input.min || 1);
      const maxValue = Number(input.max || Number.MAX_SAFE_INTEGER);
      const stepValue = Number(input.step || 1);
      let nextValue = Number(input.value || minValue);

      if (this.dataset.action === 'increase') {
        nextValue += stepValue;
      } else {
        nextValue -= stepValue;
      }

      if (nextValue < minValue) {
        nextValue = minValue;
      }
      if (nextValue > maxValue) {
        nextValue = maxValue;
      }

      input.value = String(nextValue);
    });
  });

  const menuToggle = document.querySelector('.menu-toggle');
  const navSearch = document.querySelector('.nav-search');
  const mobileMenu = document.querySelector('#mobile-menu');
  const mobileMenuPanel = document.querySelector('.mobile-menu-panel');
  const mobileMenuClose = document.querySelector('.mobile-menu-close');

  if (menuToggle) {
    const syncMenu = () => {
      const isOpen = mobileMenu && mobileMenu.classList.contains('open');
      menuToggle.setAttribute('aria-expanded', String(isOpen));
    };

    const closeMobileMenu = () => {
      if (mobileMenu) {
        mobileMenu.classList.remove('open');
        mobileMenu.setAttribute('aria-hidden', 'true');
      }
      if (menuToggle) {
        menuToggle.setAttribute('aria-expanded', 'false');
      }
      syncMenu();
    };

    menuToggle.addEventListener('click', function () {
      if (mobileMenu) {
        const willOpen = !mobileMenu.classList.contains('open');
        mobileMenu.classList.toggle('open', willOpen);
        mobileMenu.setAttribute('aria-hidden', String(!willOpen));
      }
      syncMenu();
    });

    menuToggle.addEventListener('keydown', function (event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        if (mobileMenu) {
          const willOpen = !mobileMenu.classList.contains('open');
          mobileMenu.classList.toggle('open', willOpen);
          mobileMenu.setAttribute('aria-hidden', String(!willOpen));
        }
        syncMenu();
      }
    });

    if (mobileMenuClose) {
      mobileMenuClose.addEventListener('click', closeMobileMenu);
    }

    if (mobileMenu) {
      mobileMenu.addEventListener('click', function (event) {
        if (event.target === mobileMenu) {
          closeMobileMenu();
        }
      });
    }

    document.addEventListener('click', function (event) {
      if (!mobileMenu || !mobileMenu.classList.contains('open')) {
        return;
      }

      if (event.target === menuToggle || event.target.closest('.menu-toggle')) {
        return;
      }

      if (event.target.closest('.mobile-menu-panel')) {
        return;
      }

      closeMobileMenu();
    });

    if (mobileMenuPanel) {
      mobileMenuPanel.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
          closeMobileMenu();
          if (menuToggle) {
            menuToggle.focus();
          }
        }
      });
    }

    syncMenu();
  }

  if (navSearch && menuToggle) {
    const syncNavSearch = () => {
      const isOpen = navSearch.classList.contains('mobile-open');
      menuToggle.setAttribute('aria-expanded', String(isOpen));
      navSearch.style.display = isOpen ? 'flex' : 'none';
    };

    menuToggle.addEventListener('click', function () {
      navSearch.classList.toggle('mobile-open');
      syncNavSearch();
    });

    menuToggle.addEventListener('keydown', function (event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        navSearch.classList.toggle('mobile-open');
        syncNavSearch();
      }
    });

    syncNavSearch();
  }

  const scrollSections = Array.from(document.querySelectorAll([
    'section',
    'article',
    'aside',
    'footer',
    'header',
    'main',
    '.hero-section',
    '.category-card',
    '.product-card',
    '.auth-card',
    '.auth-shell',
    '.auth-visual',
    '.auth-form-panel',
    '.cart-item',
    '.checkout-section',
    '.order-card',
    '.dashboard-card',
    '.admin-card'
  ].join(',')));

  scrollSections.forEach(function (element) {
    if (!element.classList.contains('mobile-menu') && !element.classList.contains('mobile-menu-panel')) {
      element.classList.add('scroll-reveal');
    }
  });

  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver(function (entries, observer) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -80px 0px' });

    scrollSections.forEach(function (element) {
      revealObserver.observe(element);
    });
  } else {
    scrollSections.forEach(function (element) {
      element.classList.add('visible');
    });
  }

  const userMenu = document.querySelector('.user-menu');
  const userMenuButton = document.querySelector('.user-pill');
  if (userMenu && userMenuButton) {
    const toggleUserMenu = (forceOpen) => {
      const shouldOpen = typeof forceOpen === 'boolean' ? forceOpen : !userMenu.classList.contains('open');
      userMenu.classList.toggle('open', shouldOpen);
      userMenuButton.setAttribute('aria-expanded', String(shouldOpen));
    };

    userMenuButton.addEventListener('click', function () {
      toggleUserMenu();
    });

    userMenuButton.addEventListener('keydown', function (event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        toggleUserMenu();
      }
      if (event.key === 'Escape') {
        toggleUserMenu(false);
      }
    });

    userMenu.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        toggleUserMenu(false);
        userMenuButton.focus();
      }
    });

    document.addEventListener('click', function (event) {
      if (!userMenu.contains(event.target)) {
        toggleUserMenu(false);
      }
    });
  }
});
