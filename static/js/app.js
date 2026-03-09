document.addEventListener("DOMContentLoaded", () => {
  // Carrusel manual (prev/next y arrastre)
  const carrusel = document.querySelector(".carrusel")
  const carruselContenido = document.querySelector(".carrusel-contenido")
  const btnPrev = document.querySelector(".carrusel-btn.prev")
  const btnNext = document.querySelector(".carrusel-btn.next")

  if (carrusel && carruselContenido) {
    const getCardWidth = () => {
      const card = carruselContenido.querySelector(".postre")
      if (!card) return 0
      const style = window.getComputedStyle(card)
      const gap = Number.parseFloat(window.getComputedStyle(carruselContenido).gap || "0")
      return card.offsetWidth + gap
    }

    const scrollByCards = (dir) => {
      carruselContenido.scrollBy({ left: dir * getCardWidth(), behavior: "smooth" })
    }

    btnPrev && btnPrev.addEventListener("click", () => scrollByCards(-1))
    btnNext && btnNext.addEventListener("click", () => scrollByCards(1))

    let isDown = false
    let startX = 0
    let scrollLeft = 0

    const startDrag = (x) => {
      isDown = true
      carruselContenido.classList.add("dragging")
      startX = x - carruselContenido.offsetLeft
      scrollLeft = carruselContenido.scrollLeft
    }
    const moveDrag = (x) => {
      if (!isDown) return
      const walk = x - carruselContenido.offsetLeft - startX
      carruselContenido.scrollLeft = scrollLeft - walk
    }
    const endDrag = () => {
      isDown = false
      carruselContenido.classList.remove("dragging")
    }

    // Mouse
    carruselContenido.addEventListener("mousedown", (e) => startDrag(e.pageX))
    carruselContenido.addEventListener("mousemove", (e) => moveDrag(e.pageX))
    carruselContenido.addEventListener("mouseleave", endDrag)
    carruselContenido.addEventListener("mouseup", endDrag)

    // Touch
    carruselContenido.addEventListener("touchstart", (e) => startDrag(e.touches[0].pageX), { passive: true })
    carruselContenido.addEventListener("touchmove", (e) => moveDrag(e.touches[0].pageX), { passive: true })
    carruselContenido.addEventListener("touchend", endDrag)
  }
  // Carrito
  const botones = document.querySelectorAll(".agregar-carrito")
  const modal = document.getElementById("carrito-modal")
  const cerrar = document.querySelector(".cerrar")
  const lista = document.getElementById("carrito-lista")
  const totalSpan = document.getElementById("total")
  const finalizar = document.getElementById("finalizar")

  const carrito = []
  let total = 0

  botones.forEach((btn) => {
    btn.addEventListener("click", () => {
      const postre = btn.parentElement.parentElement
      const nombre = postre.querySelector("h3").textContent
      const precio = Number.parseInt(postre.querySelector("p").textContent.replace(/\D/g, ""))

      // Verificar si el producto ya está en el carrito
      const productoExistente = carrito.find((item) => item.nombre === nombre)

      if (productoExistente) {
        productoExistente.cantidad += 1
      } else {
        carrito.push({ nombre, precio, cantidad: 1 })
      }

      actualizarCarrito()
      modal.style.display = "block"
    })
  })

  cerrar.onclick = () => {
    modal.style.display = "none"
  }

  window.onclick = (event) => {
    if (event.target == modal) {
      modal.style.display = "none"
    }
  }

  function actualizarCarrito() {
    lista.innerHTML = ""
    total = 0

    carrito.forEach((item, i) => {
      const li = document.createElement("li")
      li.className = "item-carrito"

      const infoDiv = document.createElement("div")
      infoDiv.innerHTML = `<strong>${item.nombre}</strong><br>$${item.precio} c/u`

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

      total += item.precio * item.cantidad
    })

    totalSpan.textContent = total

    finalizar.onclick = () => {
      if (carrito.length === 0) {
        alert("Tu carrito está vacío")
        return
      }
      // Guardar carrito en localStorage para la página de checkout
      localStorage.setItem("carritoCheckout", JSON.stringify(carrito))
      localStorage.setItem("totalCheckout", total)
      // Redirigir a la vista de checkout de Django
      window.location.href = "/tienda/checkout/"
    }
  }

  const formContacto = document.getElementById("form-contacto")
  if (formContacto) {
    formContacto.addEventListener("submit", (e) => {
      e.preventDefault()
      const nombre = document.getElementById("nombre").value
      const telefono = document.getElementById("telefono").value
      const mensaje = document.getElementById("mensaje").value

      // Crear mailto para envío por email
      const subject = encodeURIComponent("Consulta desde Sweet House")
      const body = encodeURIComponent(`Nombre: ${nombre}\nTeléfono: ${telefono}\nMensaje: ${mensaje}`)

      window.location.href = `mailto:contacto@sweethouse.com?subject=${subject}&body=${body}`

      // Mostrar mensaje de confirmación
      alert("¡Gracias por tu mensaje! Te contactaremos pronto.")
      formContacto.reset()
  