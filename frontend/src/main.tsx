import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import {createBrowserRouter, RouterProvider} from "react-router-dom";
import ProfilePage from "./components/ProfilePage.tsx";
import {ChakraProvider} from "@chakra-ui/react";
import SponsorLogin from "./components/SponsorLogin.tsx";
import SearchParticipant from "./components/SearchParticipant.tsx";
import RedirectHandler from "./components/RedirectHandler.tsx";
import ActivateProfile from "./components/ActivateProfile.tsx";

const router = createBrowserRouter([
    {
        path: "/",
        element: <RedirectHandler/>,
    },
    {
        path: "/activate",
        element: <ActivateProfile/>,
    },
    {
        path: "/view-profile",
        element: <ProfilePage/>,
    },
    {
        path: "/sponsor-login",
        element: <SponsorLogin/>,
    },
    {
        path: "/search-participant",
        element: <SearchParticipant/>,
    }
]);

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ChakraProvider>
            <RouterProvider router={router}/>
        </ChakraProvider>
    </StrictMode>,
)
