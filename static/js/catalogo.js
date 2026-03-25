document.addEventListener("DOMContentLoaded", () => {
  // Carrito
  const carrito = []
  let total = 0

  // Elementos del DOM
  const botonesAgregar = document.querySelectorAll(".agregar-carrito")
  const modal = document.getElementById("carrito-modal")
  const cerrar = document.querySelector(".cerrar")
  const lista = document.getElementById("carrito-lista")
  const totalSpan = document.getElementById("total")
  const finalizar = document.getElementById("finalizar")
  const verCarrito = document.getElementById("ver-carrito")
  const contadorCarrito = document.getElementById("contador-carrito")
  const irCheckout = document.getElementById("ir-checkout")

  // Botón de catálogo con menú desplegable
  const btnCatalogo = document.getElementById("btn-catalogo-dropdown")
  const dropdownMenu = document.getElementById("categoria-dropdown")
  const categoriaOptions = document.querySelectorAll(".categoria-option")
  const productosGrid = document.querySelectorAll(".catalogo-section .products-grid .product-card")
  const productosGridContainer = document.querySelector(".catalogo-section .products-grid")
  const especialesSection = document.querySelector(".especiales-section")

  // Toggle del menú desplegable
  if (btnCatalogo && dropdownMenu) {
    btnCatalogo.addEventListener("click", (e) => {
      e.stopPropagation()
      const isExpanded = btnCatalogo.getAttribute("aria-expanded") === "true"
      btnCatalogo.setAttribute("aria-expanded", !isExpanded)
      dropdownMenu.classList.toggle("show")
    })

    // Cerrar menú al hacer clic fuera
    document.addEventListener("click", (e) => {
      if (!btnCatalogo.contains(e.target) && !dropdownMenu.contains(e.target)) {
        btnCatalogo.setAttribute("aria-expanded", "false")
        dropdownMenu.classList.remove("show")
      }
    })
  }

  // Funcionalidad de filtrado
  if (categoriaOptions.length) {
    categoriaOptions.forEach((option) => {
      option.addEventListener("click", () => {
        const filtro = option.dataset.filter

        // Actualizar botón principal
        const optionText = option.querySelector("span:not(.option-icon)").textContent
        const optionIconHTML = option.querySelector(".option-icon").innerHTML
        if (btnCatalogo) {
          btnCatalogo.querySelector(".btn-text").textContent = optionText
          btnCatalogo.querySelector(".btn-icon").innerHTML = optionIconHTML
        }

        // Actualizar estado activo
        categoriaOptions.forEach((opt) => {
          opt.classList.remove("active")
        })
        option.classList.add("active")

        const effectiveFiltro = filtro

        const catalogRegulares = document.getElementById("productos-regulares")
        const categoriaSecciones = document.querySelectorAll(".categoria-seccion")
        const especialesSection = document.querySelector(".especiales-section")

        // Mostrar/ocultar sección de especiales y el grid según filtro
        if (especialesSection) {
          if (effectiveFiltro === "especiales") {
            especialesSection.style.display = "block"
            if (catalogRegulares) catalogRegulares.style.display = "none"
          } else if (effectiveFiltro === "todos") {
            especialesSection.style.display = "block"
            if (catalogRegulares) catalogRegulares.style.display = "block"
          } else {
            especialesSection.style.display = "none"
            if (catalogRegulares) catalogRegulares.style.display = "block"
          }
        }

        // Filtrar productos por sección
        if (categoriaSecciones.length > 0) {
            categoriaSecciones.forEach(sec => {
                const secCat = sec.dataset.categoriaSeccion
                const isMatch = effectiveFiltro === "todos" || secCat === effectiveFiltro
                sec.style.display = isMatch ? "" : "none"
            })
        } else {
            // Fallback para grid antiguo
            productosGrid.forEach((card) => {
              const categoria = card.dataset.categoria
              const visible = effectiveFiltro === "todos" || categoria === effectiveFiltro
              card.classList.toggle("hidden", !visible)
              card.setAttribute("aria-hidden", visible ? "false" : "true")
            })
        }

        // Cerrar menú después de seleccionar
        if (btnCatalogo && dropdownMenu) {
          btnCatalogo.setAttribute("aria-expanded", "false")
          dropdownMenu.classList.remove("show")
        }
      })
    })
  }

  // Agregar productos al carrito
  botonesAgregar.forEach((btn) => {
    btn.addEventListener("click", () => {
      const nombre = btn.getAttribute("data-nombre")
      const precio = Number.parseInt(btn.getAttribute("data-precio"))

      // Verificar si el producto ya está en el carrito
      const productoExistente = carrito.find((item) => item.nombre === nombre)

      if (productoExistente) {
        productoExistente.cantidad += 1
      } else {
        carrito.push({ nombre, precio, cantidad: 1 })
      }

      actualizarCarrito()

      // Mostrar feedback visual sin modal
      btn.style.background = "#4caf50"
      btn.textContent = "¡Agregado!"
      setTimeout(() => {
        btn.style.background = "linear-gradient(135deg, #ff4081, #e91e63)"
        btn.textContent = "Agregar al Carrito"
      }, 1000)
    })
  })

  // Mostrar carrito con productos y opciones de pago
  if (verCarrito) {
    verCarrito.addEventListener("click", () => {
      if (carrito.length === 0) {
        alert("Tu carrito está vacío")
        return
      }
      mostrarCarritoCompleto()
    })
  }

  // Cerrar modal
  if (cerrar && modal) {
    cerrar.onclick = () => {
      modal.style.display = "none"
    }
  }

  window.onclick = (event) => {
    if (modal && event.target === modal) {
      modal.style.display = "none"
    }
  }

  if (irCheckout) {
    irCheckout.addEventListener("click", () => {
      if (carrito.length === 0) {
        alert("Tu carrito está vacío")
        return
      }
      localStorage.setItem("carritoCheckout", JSON.stringify(carrito))
      localStorage.setItem("totalCheckout", total)
      window.location.href = "/tienda/checkout/"
    })
  }

  function actualizarCarrito() {
    // Actualizar contador del carrito en el header
    const totalItems = carrito.reduce((sum, item) => sum + item.cantidad, 0)
    if (contadorCarrito) {
      contadorCarrito.textContent = totalItems
    }

    // Calcular total
    total = carrito.reduce((sum, item) => sum + (item.precio * item.cantidad), 0)

    // Actualizar elementos del modal original si existen
    if (lista) {
      lista.innerHTML = ""
      carrito.forEach((item, i) => {
        const li = document.createElement("li")
        li.className = "item-carrito"

        const infoDiv = document.createElement("div")
        infoDiv.className = "item-info"
        infoDiv.innerHTML = `
          <strong>${item.nombre}</strong>
          <div>$${item.precio.toLocaleString()} c/u</div>
        `

        const controlesDiv = document.createElement("div")
        controlesDiv.className = "cantidad-controles"

        const btnMenos = document.createElement("button")
        btnMenos.textContent = "-"
        btnMenos.className = "btn-cantidad"
        btnMenos.onclick = () => {
          if (item.cantidad > 1) {
            item.cantidad -= 1
          } else {
            carrito.splice(i, 1)
          }
          actualizarCarrito()
        }

        const cantidadSpan = document.createElement("span")
        cantidadSpan.textContent = item.cantidad
        cantidadSpan.style.fontWeight = "bold"
        cantidadSpan.style.minWidth = "20px"
        cantidadSpan.style.textAlign = "center"

        const btnMas = document.createElement("button")
        btnMas.textContent = "+"
        btnMas.className = "btn-cantidad"
        btnMas.onclick = () => {
          item.cantidad += 1
          actualizarCarrito()
        }

        const btnEliminar = document.createElement("button")
        btnEliminar.textContent = "Eliminar"
        btnEliminar.className = "btn-eliminar"
        btnEliminar.onclick = () => {
          carrito.splice(i, 1)
          actualizarCarrito()
        }

        controlesDiv.appendChild(btnMenos)
        controlesDiv.appendChild(cantidadSpan)
        controlesDiv.appendChild(btnMas)
        controlesDiv.appendChild(btnEliminar)

        li.appendChild(infoDiv)
        li.appendChild(controlesDiv)
        lista.appendChild(li)
      })
    }

    if (totalSpan) {
      totalSpan.textContent = total.toLocaleString()
    }

    if (finalizar) {
      finalizar.onclick = () => {
        if (carrito.length === 0) {
          alert("Tu carrito está vacío")
          return
        }
        mostrarModalNequi()
      }
    }
  }

  function mostrarCarritoCompleto() {
    // Cerrar modal anterior si existe
    const modalAnterior = document.querySelector(".modal-carrito-completo")
    if (modalAnterior) {
      document.body.removeChild(modalAnterior)
    }

    // Crear modal del carrito completo
    const modalCarrito = document.createElement("div")
    modalCarrito.className = "modal-carrito-completo"
    modalCarrito.innerHTML = `
      <div class="modal-carrito-contenido">
        <span class="cerrar-carrito">&times;</span>
        <h2>🛒 Tu Carrito de Compras</h2>
        <div class="carrito-productos" id="lista-carrito-completo"></div>
        <div class="carrito-total-completo">
          <h3>Total: $<span id="total-completo">0</span></h3>
        </div>
        <div class="opciones-pago">
          <h3>💳 Opciones de Pago</h3>
          <div class="metodos-pago">
            <button class="btn-pago-nequi" onclick="mostrarPagoNequi()">
              <img src="./img/nequi_logo.png" alt="Nequi" style="width: 30px; height: 30px;">
              Pagar con Nequi
            </button>
            <button class="btn-pago-qr" onclick="mostrarQR()">
              📱 Pagar con QR
            </button>
          </div>
        </div>
      </div>
    `

    document.body.appendChild(modalCarrito)
    modalCarrito.style.display = "block"

    // Llenar la lista de productos
    const listaCompleta = document.getElementById("lista-carrito-completo")
    const totalCompleto = document.getElementById("total-completo")
    let totalCalculado = 0

    carrito.forEach((item, i) => {
      const productoDiv = document.createElement("div")
      productoDiv.className = "producto-carrito-completo"
      productoDiv.innerHTML = `
        <div class="info-producto">
          <h4>${item.nombre}</h4>
          <p>$${item.precio.toLocaleString()} c/u</p>
        </div>
        <div class="controles-producto">
          <button class="btn-menos" onclick="cambiarCantidad(${i}, -1)">-</button>
          <span class="cantidad">${item.cantidad}</span>
          <button class="btn-mas" onclick="cambiarCantidad(${i}, 1)">+</button>
          <button class="btn-eliminar" onclick="eliminarProducto(${i})">🗑️</button>
        </div>
        <div class="subtotal">$${(item.precio * item.cantidad).toLocaleString()}</div>
      `
      listaCompleta.appendChild(productoDiv)
      totalCalculado += item.precio * item.cantidad
    })

    totalCompleto.textContent = totalCalculado.toLocaleString()

    // Cerrar modal
    modalCarrito.querySelector(".cerrar-carrito").onclick = () => {
      document.body.removeChild(modalCarrito)
    }

    // Cerrar al hacer clic fuera del modal
    modalCarrito.onclick = (e) => {
      if (e.target === modalCarrito) {
        document.body.removeChild(modalCarrito)
      }
    }
  }

  // Funciones globales para el carrito completo
  window.cambiarCantidad = (index, cambio) => {
    if (carrito[index]) {
      carrito[index].cantidad += cambio
      if (carrito[index].cantidad <= 0) {
        carrito.splice(index, 1)
      }
      actualizarCarrito()
      // Refrescar el modal del carrito completo si está abierto
      const modalCarrito = document.querySelector(".modal-carrito-completo")
      if (modalCarrito) {
        mostrarCarritoCompleto()
      }
    }
  }

  window.eliminarProducto = (index) => {
    if (carrito[index]) {
      carrito.splice(index, 1)
      actualizarCarrito()
      // Refrescar el modal del carrito completo si está abierto
      const modalCarrito = document.querySelector(".modal-carrito-completo")
      if (modalCarrito) {
        mostrarCarritoCompleto()
      }
    }
  }

  window.mostrarPagoNequi = () => {
    // Cerrar modal del carrito
    const modalCarrito = document.querySelector(".modal-carrito-completo")
    if (modalCarrito) {
      document.body.removeChild(modalCarrito)
    }
    mostrarModalNequi()
  }

  window.mostrarQR = () => {
    // Cerrar modal del carrito
    const modalCarrito = document.querySelector(".modal-carrito-completo")
    if (modalCarrito) {
      document.body.removeChild(modalCarrito)
    }
    mostrarModalQR()
  }

  function mostrarModalQR() {
    const modalQR = document.createElement("div")
    modalQR.className = "modal-qr"
    modalQR.innerHTML = `
      <div class="modal-qr-contenido">
        <span class="cerrar-qr">&times;</span>
        <h3>📱 Pago con QR</h3>
        <div class="qr-info">
          <div class="qr-code">
            <div class="qr-placeholder">
              <p>🔲</p>
              <p>QR Code</p>
              <p>Nequi</p>
            </div>
          </div>
          <div class="qr-datos">
            <p><strong>Total a pagar: $${total.toLocaleString()}</strong></p>
            <div class="instrucciones-qr">
              <h4>Instrucciones:</h4>
              <ol>
                <li>Abre tu app Nequi</li>
                <li>Selecciona "Escanear QR"</li>
                <li>Escanea este código</li>
                <li>Confirma el pago</li>
                <li>Toma captura del comprobante</li>
              </ol>
            </div>
            <button class="btn-confirmar-qr">Confirmar Pago</button>
          </div>
        </div>
      </div>
    `

    document.body.appendChild(modalQR)
    modalQR.style.display = "block"

    // Cerrar modal
    modalQR.querySelector(".cerrar-qr").onclick = () => {
      document.body.removeChild(modalQR)
    }

    // Confirmar pago
    modalQR.querySelector(".btn-confirmar-qr").onclick = () => {
      alert("¡Gracias por tu compra! Te contactaremos pronto para confirmar tu pedido.")
      carrito.length = 0
      actualizarCarrito()
      document.body.removeChild(modalQR)
    }
  }

  function mostrarModalNequi() {
    const modalNequi = document.createElement("div")
    modalNequi.className = "modal-nequi"
    modalNequi.innerHTML = `
      <div class="modal-nequi-contenido">
        <span class="cerrar-nequi">&times;</span>
        <h3>💳 Pagar con Nequi</h3>
        <div class="nequi-info">
          <img src="./img/nequi-logo.png" alt="Nequi" class="nequi-logo">
          <p><strong>Total a pagar: $${total.toLocaleString()}</strong></p>
          <div class="nequi-datos">
            <p>📱 <strong>Número Nequi:</strong> 301 509 6797</p>
            <p>👤 <strong>Nombre:</strong> Sweet House</p>
          </div>
          <div class="instrucciones">
            <h4>Instrucciones:</h4>
            <ol>
              <li>Abre tu app Nequi</li>
              <li>Selecciona "Enviar plata"</li>
              <li>Ingresa el número: <strong>301 509 6797</strong></li>
              <li>Envía: <strong>$${total.toLocaleString()}</strong></li>
              <li>Toma captura del comprobante</li>
            </ol>
          </div>
          <button class="btn-confirmar">Confirmar Pago</button>
        </div>
      </div>
    `

    document.body.appendChild(modalNequi)
    modalNequi.style.display = "block"

    // Cerrar modal
    modalNequi.querySelector(".cerrar-nequi").onclick = () => {
      document.body.removeChild(modalNequi)
    }

    // Confirmar pago
    modalNequi.querySelector(".btn-confirmar").onclick = () => {
      alert("¡Gracias por tu compra! Te contactaremos pronto para confirmar tu pedido.")
      carrito.length = 0
      actualizarCarrito()
      document.body.removeChild(modalNequi)
      if (modal) {
        modal.style.display = "none"
      }
    }
  }

  // Inicializar contador
  actualizarCarrito()

  // ── Modal de ingredientes: mostrar al hacer hover por 3 segundos ──
  const ingredientsModal = document.getElementById("ingredients-modal")
  const modalTitle = document.getElementById("ingredients-modal-title")
  const modalDesc = document.getElementById("ingredients-modal-desc")
  const modalList = document.getElementById("ingredients-modal-list")
  let hoverTimer = null

  function showIngredientsInsideCard(card) {
    const raw = card.dataset.ingredients || ""
    const name = card.dataset.productName || ""
    const desc = card.dataset.description || ""
    if (!raw.trim() && !desc.trim()) return

    // Poblar título
    modalTitle.textContent = name

    // Poblar descripción
    if (desc.trim()) {
      modalDesc.textContent = desc
      modalDesc.style.display = "block"
    } else {
      modalDesc.style.display = "none"
    }

    // Poblar lista de ingredientes
    modalList.innerHTML = ""
    if (raw.trim()) {
      const items = raw.split(/[,;\n]+/).map(s => s.trim()).filter(s => s.length > 0)
      items.forEach(item => {
        const li = document.createElement("li")
        li.textContent = item
        modalList.appendChild(li)
      })
    }

    const rect = card.getBoundingClientRect();
    const modalWidth = 320;
    let leftPos = rect.right + 15;
    
    // Si se sale de la pantalla por la derecha, mostrarlo por la izquierda
    if (leftPos + modalWidth > window.innerWidth) {
      leftPos = rect.left - modalWidth - 15;
    }
    
    // Si aún así no cabe o es móvil, ponerlo centrado
    if (leftPos < 0 || window.innerWidth <= 768) {
      leftPos = (window.innerWidth - modalWidth) / 2;
    }

    // Insertar el modal en el body
    document.body.appendChild(ingredientsModal);

    // Ajustar estilos para ventana flotante
    ingredientsModal.style.position = "fixed";
    ingredientsModal.style.top = Math.max(20, rect.top) + "px";
    ingredientsModal.style.left = Math.max(10, leftPos) + "px";
    ingredientsModal.style.right = "auto";
    ingredientsModal.style.bottom = "auto";
    ingredientsModal.style.width = modalWidth + "px";
    ingredientsModal.style.height = "auto";
    ingredientsModal.style.maxHeight = "90vh";
    ingredientsModal.style.overflowY = "auto";
    ingredientsModal.style.borderRadius = "16px";
    ingredientsModal.style.zIndex = "9999";
    ingredientsModal.style.visibility = "visible";
    ingredientsModal.style.margin = "0"; // Asegurar que no haya márgenes que lo descuadren

    ingredientsModal.classList.add("show")
  }

  function hideIngredientsModal() {
    ingredientsModal.classList.remove("show")
  }

  const cards = document.querySelectorAll(".product-card")
  cards.forEach(card => {
    // Al entrar (hover o tap en móvil), iniciamos el contador de 3 segundos
    const handleEnter = () => {
      if (hoverTimer) clearTimeout(hoverTimer);
      hoverTimer = setTimeout(() => {
        showIngredientsInsideCard(card);
      }, 3000); // 3 segundos
    };

    // Al salir, cancelamos el contador y ocultamos
    const handleLeave = () => {
      if (hoverTimer) clearTimeout(hoverTimer);
      hideIngredientsModal();
    };

    card.addEventListener("mouseenter", handleEnter);
    card.addEventListener("mouseleave", handleLeave);
  })

})
