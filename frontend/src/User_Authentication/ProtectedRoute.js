// You want to protect certain routes so that only authenticated users can access them.
import React from "react";
import { Navigate } from "react-router-dom";
import { UserAuthentication } from "./LoginContext";

const ProtectedRoute = ({ children }) => {
  const { user } = UserAuthentication();

  // While checking user state, don't render anything
  if (user === undefined) return null; 

  // If no user, redirect to login page so that they cannot access protected routes 
  // like dashboard or report generator without logging in
  if (!user) return <Navigate to="/login" replace />;
  return children;
};

export default ProtectedRoute;
