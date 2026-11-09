/*
 * Mejoras opcionales de la interfaz. La aplicación funciona sin JavaScript.
 * - Menú lateral en tablet y móvil: abrir, cerrar con Escape, el fondo o el
 *   botón, y devolver el foco al botón al cerrar.
 */
(function () {
    'use strict';

    var body = document.body;
    var boton = document.querySelector('[data-sidebar-toggle]');
    var sidebar = document.getElementById('sidebar');
    var fondo = document.querySelector('[data-sidebar-backdrop]');
    if (!boton || !sidebar || !fondo) { return; }

    var escritorio = window.matchMedia('(min-width: 1024px)');

    function abierto() { return body.classList.contains('sidebar-open'); }

    function abrir() {
        body.classList.add('sidebar-open');
        boton.setAttribute('aria-expanded', 'true');
        boton.setAttribute('aria-label', 'Cerrar menú');
        fondo.hidden = false;
        var primerEnlace = sidebar.querySelector('a, button');
        if (primerEnlace) { primerEnlace.focus(); }
    }

    function cerrar(devolverFoco) {
        body.classList.remove('sidebar-open');
        boton.setAttribute('aria-expanded', 'false');
        boton.setAttribute('aria-label', 'Abrir menú');
        fondo.hidden = true;
        if (devolverFoco) { boton.focus(); }
    }

    boton.addEventListener('click', function () {
        if (abierto()) { cerrar(true); } else { abrir(); }
    });

    fondo.addEventListener('click', function () { cerrar(true); });

    document.addEventListener('keydown', function (evento) {
        if (evento.key === 'Escape' && abierto()) { cerrar(true); }
    });

    // Al pasar a escritorio el menú queda fijo: se limpia el estado móvil.
    escritorio.addEventListener('change', function (e) {
        if (e.matches && abierto()) { cerrar(false); }
    });
})();
