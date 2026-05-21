from abc import ABC, abstractmethod


class ComponenteBase(ABC):
    def __init__(self, titulo):
        self.titulo = titulo

    @abstractmethod
    def render(self):
        pass


class BarraNivelAgua(ComponenteBase):
    def __init__(self, titulo, porcentaje):
        super().__init__(titulo)

        if porcentaje < 0:
            porcentaje = 0
        if porcentaje > 100:
            porcentaje = 100

        self.porcentaje = porcentaje

    def obtener_color(self):
        if self.porcentaje <= 20:
            return "#d32f2f"
        elif self.porcentaje <= 50:
            return "#f9a825"
        else:
            return "#388e3c"

    def obtener_estado(self):
        if self.porcentaje <= 20:
            return "Nivel crítico"
        elif self.porcentaje <= 50:
            return "Nivel medio"
        else:
            return "Nivel bueno"

    def render(self):
        color = self.obtener_color()
        estado = self.obtener_estado()

        return f"""
        <div class="card">
            <h2>{self.titulo}</h2>

            <div class="nivel-numero">{self.porcentaje}%</div>

            <div class="barra-contenedor">
                <div class="barra-relleno" style="width:{self.porcentaje}%; background:{color};"></div>
            </div>

            <div class="estado" style="color:{color};">
                {estado}
            </div>
        </div>
        """