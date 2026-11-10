/*
 * Mejoras opcionales de la interfaz. La aplicación funciona sin JavaScript.
 * 1. Menú lateral en tablet y móvil.
 * 2. Mostrar u ocultar contraseñas.
 * 3. Asociar ayuda y errores a cada campo (aria-describedby, aria-invalid).
 */
(function () {
    'use strict';

    /* 1. Menú lateral ---------------------------------------------------- */
    function iniciarMenuLateral() {
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
    }

    /* 2. Mostrar u ocultar contraseñas ----------------------------------- */
    function iniciarContrasenas() {
        document.querySelectorAll('[data-password-toggle]').forEach(function (boton) {
            var campo = document.getElementById(boton.getAttribute('aria-controls'));
            if (!campo) { return; }
            boton.hidden = false;
            boton.addEventListener('click', function () {
                var mostrar = campo.type === 'password';
                campo.type = mostrar ? 'text' : 'password';
                boton.setAttribute('aria-pressed', mostrar ? 'true' : 'false');
                boton.setAttribute('aria-label', mostrar ? 'Ocultar contraseña' : 'Mostrar contraseña');
            });
        });
    }

    /* 3. Ayuda y errores accesibles -------------------------------------- */
    function iniciarDescripcionesDeCampos() {
        document.querySelectorAll('[data-field]').forEach(function (bloque) {
            var campo = bloque.querySelector('input, select, textarea');
            if (!campo) { return; }
            var ids = [];
            bloque.querySelectorAll('.field__errors[id], .helptext[id]').forEach(function (el) { ids.push(el.id); });
            if (ids.length) { campo.setAttribute('aria-describedby', ids.join(' ')); }
            if (bloque.classList.contains('field--error')) { campo.setAttribute('aria-invalid', 'true'); }
        });
    }

    iniciarMenuLateral();
    iniciarContrasenas();
    iniciarDescripcionesDeCampos();
})();
