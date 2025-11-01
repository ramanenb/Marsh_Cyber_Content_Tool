// Handles user authentication state and provides login functionality across the app
import { createContext, useContext, useEffect, useState, useReducer } from 'react';
import { signInWithEmailAndPassword, onAuthStateChanged, setPersistence, browserSessionPersistence } from "firebase/auth";
import { auth } from "./firebase_setup";

const UserContext = createContext(null);

// creating useContext Hook
export const LoginContextProvider = ({children}) => {

    /* FIREBASE FUNCTIONS & USER */
    // user object 
    const [user, setUser] = useState({});
    const [loading, setLoading] = useState(true);

    // Set persistence on mount so that the END user is logged out upon closing the tab or browser
    // if not specified, firebase still rmbrs the login user and they can access the links easily
    useEffect(() => {
        setPersistence(auth, browserSessionPersistence)
            .catch((error) => {
                console.error("Error setting persistence:", error);
            });
    }, []);

    // login firebase function
    const login = (email, password) =>  {
        return signInWithEmailAndPassword(auth, email, password);
    }

    // updating user object when there is a state change to User 
    useEffect(() => {
        const subscribe = onAuthStateChanged(auth, (currentUser) => {
          setUser(currentUser);
          setLoading(false);
        });
        return () => {
          subscribe();
        };
    }, []);

    // make the props passed to all children neater 
    const loginContextValue = {
        // user & login page functions
        user, login, loading
    };

    return (
        // pass down User object and signup,loginmlogout function as props
        <UserContext.Provider value={loginContextValue}>
            { children }
        </UserContext.Provider>
    );
}

// exporting the context out 
export const UserAuthentication = () => {
    return useContext(UserContext);
}