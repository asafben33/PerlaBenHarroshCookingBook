/* ═══════════════════════════════════════════════════════════════════════
   ABOUT REDESIGNED — JavaScript
   ═══════════════════════════════════════════════════════════════════════
   הסבר: JS לסעיף "אודות" המחודש. כולל:
   1. IntersectionObserver לאנימציות reveal-on-scroll
   2. Gallery Builder - טעינה דינמית של כל תמונות הספר (151+)
   3. Lightbox Modal - צפייה בתמונה מלאה עם מקלדת ומגע
   4. Family Tree - D3.js אינטראקטיבי (עם fallback ל-SVG טבעי)
   5. Show/Hide logic - לחיבור עם כפתור "אודות" הקיים
   
   Version: 1.0 (2026-04-18)
   Author: עבור אסף יעקב בן-הראש
   ═══════════════════════════════════════════════════════════════════════
*/

(function () {
  'use strict';

  // ═══════════════════════════════════════════════════════════════════
  // 0. SHOW/HIDE LOGIC — מציג את הסעיף המחודש כשה-#about מורחב
  // ═══════════════════════════════════════════════════════════════════
  function syncAboutVisibility() {
    var about = document.getElementById('about');
    var redesigned = document.getElementById('about-redesigned');
    if (!about || !redesigned) return;

    var expanded = about.getAttribute('aria-hidden') === 'false';
    if (expanded) {
      redesigned.classList.add('ar-active');
      // Init content on first show
      if (!redesigned.dataset.inited) {
        initRedesigned();
        redesigned.dataset.inited = '1';
      }
    } else {
      redesigned.classList.remove('ar-active');
    }
  }

  // Watch for aria-hidden changes on #about
  function watchAbout() {
    var about = document.getElementById('about');
    if (!about) return;
    new MutationObserver(syncAboutVisibility)
      .observe(about, { attributes: true, attributeFilter: ['aria-hidden'] });
    syncAboutVisibility(); // initial check
  }

  // ═══════════════════════════════════════════════════════════════════
  // 1. REVEAL-ON-SCROLL (IntersectionObserver)
  // ═══════════════════════════════════════════════════════════════════
  function initReveal() {
    if (!('IntersectionObserver' in window)) {
      document.querySelectorAll('.ar-reveal').forEach(function (el) {
        el.classList.add('ar-visible');
      });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('ar-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -80px 0px' });
    document.querySelectorAll('#about-redesigned .ar-reveal').forEach(function (el) {
      io.observe(el);
    });
  }

  // ═══════════════════════════════════════════════════════════════════
  // 2. GALLERY BUILDER — בונה את גלריית כל תמונות הספר
  // ═══════════════════════════════════════════════════════════════════
  // List of all known book images - will try to load all and gracefully
  // skip any that don't exist on the server.
  var ALL_BOOK_IMAGES = [];
  
  // Build complete list: g42 series (000-099) + g45 series (000-099)
  // The onerror handler will skip any that don't exist.
  for (var i = 0; i < 100; i++) {
    var pad = (i < 10 ? '00' : (i < 100 ? '0' : '')) + i;
    ALL_BOOK_IMAGES.push('book_g42_' + pad + '.jpg');
    ALL_BOOK_IMAGES.push('book_g45_' + pad + '.jpg');
  }

  var GALLERY_BATCH_SIZE = 24;
  var galleryLoadedCount = 0;
  var galleryAvailableImages = [];
  var galleryStateChecked = false;

  function checkImageExists(src) {
    return new Promise(function (resolve) {
      var img = new Image();
      img.onload = function () { resolve({ src: src, exists: true, w: img.naturalWidth, h: img.naturalHeight }); };
      img.onerror = function () { resolve({ src: src, exists: false }); };
      img.src = src;
    });
  }

  function buildGalleryItem(filename, index) {
    var item = document.createElement('figure');
    item.className = 'ar-gallery-item';
    item.setAttribute('tabindex', '0');
    item.setAttribute('role', 'button');
    item.setAttribute('aria-label', 'תמונה ' + (index + 1) + ' מתוך הספר');
    item.dataset.src = 'images/book_images/' + filename;
    item.dataset.index = index;

    var img = document.createElement('img');
    img.src = 'images/book_images/' + filename;
    img.alt = 'תמונה מהספר "על שביל האהבה ממרוקו לירושלים"';
    img.loading = 'lazy';
    img.decoding = 'async';
    img.addEventListener('load', function () {
      img.classList.add('ar-loaded');
    });
    img.addEventListener('error', function () {
      item.style.display = 'none';
    });

    item.appendChild(img);

    // Click/keyboard -> lightbox
    item.addEventListener('click', function () { openLightbox(index); });
    item.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openLightbox(index);
      }
    });

    return item;
  }

  function renderGalleryBatch() {
    var grid = document.getElementById('ar-gallery-grid');
    if (!grid) return;
    
    var start = galleryLoadedCount;
    var end = Math.min(start + GALLERY_BATCH_SIZE, galleryAvailableImages.length);
    
    for (var i = start; i < end; i++) {
      var item = buildGalleryItem(galleryAvailableImages[i], i);
      grid.appendChild(item);
    }
    galleryLoadedCount = end;

    // Hide button if no more
    var btn = document.getElementById('ar-gallery-load-more');
    if (btn && galleryLoadedCount >= galleryAvailableImages.length) {
      btn.style.display = 'none';
    }
  }

  function initGallery() {
    var grid = document.getElementById('ar-gallery-grid');
    if (!grid || galleryStateChecked) return;
    galleryStateChecked = true;

    // Quick approach: assume most exist, render them, onerror hides missing ones
    galleryAvailableImages = ALL_BOOK_IMAGES.slice();
    renderGalleryBatch();

    var btn = document.getElementById('ar-gallery-load-more');
    if (btn) {
      btn.addEventListener('click', renderGalleryBatch);
    }
  }

  // ═══════════════════════════════════════════════════════════════════
  // 3. LIGHTBOX
  // ═══════════════════════════════════════════════════════════════════
  var currentLbIndex = 0;
  var lbSources = []; // populated from gallery

  function collectLightboxSources() {
    lbSources = [];
    var items = document.querySelectorAll('#ar-gallery-grid .ar-gallery-item');
    items.forEach(function (item) {
      if (item.style.display !== 'none') {
        lbSources.push({
          src: item.dataset.src,
          alt: item.querySelector('img').alt
        });
      }
    });
  }

  function openLightbox(index) {
    collectLightboxSources();
    if (!lbSources.length) return;
    currentLbIndex = Math.max(0, Math.min(index, lbSources.length - 1));
    showLightboxImage();
    var lb = document.getElementById('ar-lightbox');
    lb.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    // Focus trap: move focus to close button
    setTimeout(function () {
      var closeBtn = document.getElementById('ar-lb-close');
      if (closeBtn) closeBtn.focus();
    }, 100);
  }

  function closeLightbox() {
    var lb = document.getElementById('ar-lightbox');
    lb.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  function showLightboxImage() {
    var img = document.getElementById('ar-lb-img');
    var cap = document.getElementById('ar-lb-caption');
    if (!lbSources[currentLbIndex]) return;
    img.src = lbSources[currentLbIndex].src;
    img.alt = lbSources[currentLbIndex].alt;
    cap.textContent = (currentLbIndex + 1) + ' / ' + lbSources.length;
  }

  function nextLb() {
    currentLbIndex = (currentLbIndex + 1) % lbSources.length;
    showLightboxImage();
  }

  function prevLb() {
    currentLbIndex = (currentLbIndex - 1 + lbSources.length) % lbSources.length;
    showLightboxImage();
  }

  function initLightbox() {
    var close = document.getElementById('ar-lb-close');
    var next = document.getElementById('ar-lb-next');
    var prev = document.getElementById('ar-lb-prev');
    var lb = document.getElementById('ar-lightbox');
    if (!close || !next || !prev || !lb) return;

    close.addEventListener('click', closeLightbox);
    next.addEventListener('click', nextLb);
    prev.addEventListener('click', prevLb);
    lb.addEventListener('click', function (e) {
      if (e.target === lb) closeLightbox();
    });
    document.addEventListener('keydown', function (e) {
      if (lb.getAttribute('aria-hidden') !== 'false') return;
      if (e.key === 'Escape') closeLightbox();
      else if (e.key === 'ArrowLeft') nextLb();   // RTL: left = next
      else if (e.key === 'ArrowRight') prevLb();  // RTL: right = prev
    });

    // Touch swipe support
    var touchStartX = 0;
    lb.addEventListener('touchstart', function (e) {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      var dx = e.changedTouches[0].screenX - touchStartX;
      if (Math.abs(dx) > 50) {
        if (dx > 0) prevLb(); else nextLb();
      }
    }, { passive: true });
  }

  // ═══════════════════════════════════════════════════════════════════
  // 4. FAMILY TREE (Native SVG — no D3 dependency)
  // ═══════════════════════════════════════════════════════════════════
  // Tree data model
  var TREE_DATA = {
    name: 'פרלה ופנחס',
    years: '1927 — 2025',
    gen: 'root',
    children: [
      {
        name: 'סימי',
        years: 'b. 1953',
        gen: 'gen1',
        spouse: 'יהודה ינאי',
        children: [
          { name: 'יאיר', gen: 'gen2' },
          { name: 'אליענה', gen: 'gen2' },
          { name: 'כנרת', gen: 'gen2' },
          { name: 'איתמר ומעיין', gen: 'gen2' }
        ]
      },
      {
        name: 'יהודה',
        years: 'b. 1956',
        gen: 'gen1',
        children: [
          { name: 'ניר', gen: 'gen2' },
          { name: 'בועז', gen: 'gen2' },
          { name: 'רעות', gen: 'gen2' },
          { name: 'ענבר', gen: 'gen2' }
        ]
      },
      {
        name: 'סמי',
        years: 'b. 1960',
        gen: 'gen1',
        spouse: 'דבי',
        location: 'לונדון',
        children: [
          { name: 'טליה', gen: 'gen2' },
          { name: 'סופי', gen: 'gen2' },
          { name: 'אדם', gen: 'gen2' },
          { name: 'דיוויד', gen: 'gen2' }
        ]
      },
      {
        name: 'אילן',
        years: 'b. 1964',
        gen: 'gen1',
        spouse: 'דנה',
        location: 'תל-אביב',
        children: [
          { name: 'איתי', gen: 'gen2' },
          { name: 'נועה', gen: 'gen2' },
          { name: 'נעמה', gen: 'gen2' }
        ]
      },
      {
        name: 'אסף',
        years: 'b. 1974',
        gen: 'gen1',
        spouse: 'אילנית',
        location: 'מבשרת',
        children: [
          { name: 'נועם', gen: 'gen2' },
          { name: 'הדר', gen: 'gen2' },
          { name: 'יובל', gen: 'gen2' }
        ]
      }
    ]
  };

  function initFamilyTree() {
    var container = document.getElementById('ar-family-tree');
    if (!container) return;

    var width = container.clientWidth || 800;
    var height = 620;
    // Calculate layout
    var rootX = width / 2;
    var rootY = 70;
    var gen1Y = 240;
    var gen2Y = 440;

    var numGen1 = TREE_DATA.children.length;
    var gen1Spacing = (width - 80) / numGen1;

    var svgNS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', height);
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', 'עץ משפחת בן הראש — 3 דורות');

    // ----- Draw links (lines) first, so they sit under nodes -----
    var linksGroup = document.createElementNS(svgNS, 'g');
    linksGroup.setAttribute('class', 'ar-tree-links');

    TREE_DATA.children.forEach(function (child, idx) {
      var childX = 40 + gen1Spacing * (idx + 0.5);
      // Root -> gen1
      var link = document.createElementNS(svgNS, 'path');
      link.setAttribute('class', 'ar-tree-link');
      var midY = (rootY + gen1Y) / 2;
      link.setAttribute('d', 'M ' + rootX + ',' + (rootY + 30) +
        ' C ' + rootX + ',' + midY + ' ' + childX + ',' + midY +
        ' ' + childX + ',' + (gen1Y - 22));
      linksGroup.appendChild(link);

      // gen1 -> gen2
      if (child.children && child.children.length) {
        var numChildren = child.children.length;
        var childSpacing = Math.min(gen1Spacing - 20, 150) / numChildren;
        child.children.forEach(function (grand, gIdx) {
          var grandX = childX - (numChildren - 1) * childSpacing / 2 + gIdx * childSpacing;
          var glink = document.createElementNS(svgNS, 'path');
          glink.setAttribute('class', 'ar-tree-link');
          var gmidY = (gen1Y + gen2Y) / 2;
          glink.setAttribute('d', 'M ' + childX + ',' + (gen1Y + 22) +
            ' C ' + childX + ',' + gmidY + ' ' + grandX + ',' + gmidY +
            ' ' + grandX + ',' + (gen2Y - 15));
          linksGroup.appendChild(glink);
        });
      }
    });
    svg.appendChild(linksGroup);

    // ----- Helper: create a node group -----
    function createNode(cx, cy, label, subLabel, genClass, radius) {
      var g = document.createElementNS(svgNS, 'g');
      g.setAttribute('class', 'ar-tree-node ar-tree-node-' + genClass);
      g.setAttribute('transform', 'translate(' + cx + ',' + cy + ')');

      var c = document.createElementNS(svgNS, 'circle');
      c.setAttribute('r', radius);
      c.setAttribute('cx', 0);
      c.setAttribute('cy', 0);
      g.appendChild(c);

      var t1 = document.createElementNS(svgNS, 'text');
      t1.setAttribute('class', 'ar-tree-label');
      t1.setAttribute('x', 0);
      t1.setAttribute('y', radius + 18);
      t1.setAttribute('text-anchor', 'middle');
      t1.textContent = label;
      g.appendChild(t1);

      if (subLabel) {
        var t2 = document.createElementNS(svgNS, 'text');
        t2.setAttribute('class', 'ar-tree-label-year');
        t2.setAttribute('x', 0);
        t2.setAttribute('y', radius + 33);
        t2.setAttribute('text-anchor', 'middle');
        t2.textContent = subLabel;
        g.appendChild(t2);
      }
      return g;
    }

    // ----- Draw Root -----
    var rootNode = createNode(rootX, rootY, TREE_DATA.name, TREE_DATA.years, 'root', 30);
    svg.appendChild(rootNode);

    // ----- Draw Gen1 (children) -----
    TREE_DATA.children.forEach(function (child, idx) {
      var childX = 40 + gen1Spacing * (idx + 0.5);
      var spouseLabel = '';
      if (child.spouse) spouseLabel = child.spouse;
      if (child.location) spouseLabel += (spouseLabel ? ' — ' : '') + child.location;
      var mainLabel = child.name + (child.spouse ? ' + ' + child.spouse : '');
      var subLabel = child.years + (child.location ? ' · ' + child.location : '');
      
      var node = createNode(childX, gen1Y, child.name, child.years, 'gen1', 22);
      svg.appendChild(node);

      // Draw gen2
      if (child.children && child.children.length) {
        var numChildren = child.children.length;
        var childSpacing = Math.min(gen1Spacing - 20, 150) / numChildren;
        child.children.forEach(function (grand, gIdx) {
          var grandX = childX - (numChildren - 1) * childSpacing / 2 + gIdx * childSpacing;
          var grandNode = createNode(grandX, gen2Y, grand.name, '', 'gen2', 15);
          svg.appendChild(grandNode);
        });
      }
    });

    container.innerHTML = '';
    container.appendChild(svg);

    // Pan & Zoom basic (optional)
    var isDragging = false, startX = 0, startY = 0, vbX = 0, vbY = 0;
    svg.addEventListener('mousedown', function (e) {
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
    });
    window.addEventListener('mousemove', function (e) {
      if (!isDragging) return;
      var dx = e.clientX - startX;
      var dy = e.clientY - startY;
      vbX -= dx * 1.5;
      vbY -= dy * 1.5;
      svg.setAttribute('viewBox', vbX + ' ' + vbY + ' ' + width + ' ' + height);
      startX = e.clientX;
      startY = e.clientY;
    });
    window.addEventListener('mouseup', function () { isDragging = false; });
  }

  // ═══════════════════════════════════════════════════════════════════
  // MAIN INIT
  // ═══════════════════════════════════════════════════════════════════
  function initRedesigned() {
    try {
      initReveal();
      initGallery();
      initLightbox();
      initFamilyTree();
    } catch (err) {
      console.error('About Redesigned init error:', err);
    }
  }

  // Start
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', watchAbout);
  } else {
    watchAbout();
  }
})();
