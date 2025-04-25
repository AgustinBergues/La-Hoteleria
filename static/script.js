function actualizarPrecio() {
    const select = document.getElementById("hotel");
    
    fetch('/static/hotels.json')
        .then(response => response.json())
        .then(data => {
          // Obtener el id del hotel desde el atributo data-hotel-id del elemento con id "hotel-info"
          const hotelId = document.getElementById('hotel-info').getAttribute('data-hotel-id');
        
          // Buscar el hotel con ese id
          const hotel = data.find(hotel => hotel.id === parseInt(hotelId));
        
          if (hotel) {
            if  (select.value === "Simple") {
                document.getElementById('precio-habitacion').textContent = `Precio de Habitacion: $${hotel.precios.Simple}`;
                precioHabitacion = hotel.precios.Simple;}
            if  (select.value === "Doble") {
                document.getElementById('precio-habitacion').textContent = `Precio de Habitacion: $${hotel.precios.Doble}`;
                precioHabitacion = hotel.precios.Doble;}
            if  (select.value === "Suite") {
                document.getElementById('precio-habitacion').textContent = `Precio de Habitacion: $${hotel.precios.Suite}`;
                precioHabitacion = hotel.precios.Suite;}

            let total = precioHabitacion + 15;
            document.getElementById('precio-impuesto').textContent = `Impuestos: $15`;
            document.getElementById('precio-total').textContent = `Total: $`+ total;

            
            

          } else {
            console.log('Hotel no encontrado');
          }
        })
        .catch(error => {
          console.error('Error al cargar el archivo JSON:', error);
        });

    
    document.getElementById("precio-total").textContent = precio;
}


window.onload = actualizarPrecio;   