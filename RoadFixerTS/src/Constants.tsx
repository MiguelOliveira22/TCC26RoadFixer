import { type RouteObject } from "react-router"
import InicioPage from "./implementations/layouts/inicio/InicioPage"

export const nomeProjeto = "RoadFixer";

export const apiPath = "http://127.0.0.1:8000/";

export const routing: RouteObject = {
    path: "/",
    Component: <InicioPage />,
    children: [
        { path: "/monitoramento", Component: },
        { path: "/saiba-mais", Component: },
        { path: "/estatisticas", Component: }
    ]
};
