/**
=========================================================================
* Sign In Page 
=========================================================================
*/

import React, { useState } from "react";
import { UserAuthentication } from "./LoginContext";
import { Link, useNavigate } from "react-router-dom";

import {
  Button,
  TextField,
  Paper,
  Box,
  Grid,
  Typography
} from "@mui/material";

import bgImage from "assets/images/bg-reset-cover.jpeg";
import MarshLogoImage from "assets/images/logos/Marsh_logo_noBG.png";

import Stack from '@mui/material/Stack';
import EqualizerIcon from '@mui/icons-material/Equalizer';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import SwitchAccessShortcutAddIcon from '@mui/icons-material/SwitchAccessShortcutAdd';

export default function SignInSide() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMess, setErrorMess] = useState("");
  const [modal, setModal] = useState(false);

  // login functionality taken from LoginContext file
  const { login } = UserAuthentication();
  const navigate = useNavigate();
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate("/dashboard/Marsh");
    } catch (e) {
      setErrorMess(String(e).substring(24));
      setModal(true);
      console.error("Login error:", e);
    }
  };

  // data to be fed into the left side explanation boxes of the Login Page
  const items = [
    {
        icon: <SwitchAccessShortcutAddIcon sx={{ color: 'navy' }} />,
        title: '[UPCOMING] Feature x',
        description:'Feature x description',
    },
    {
        icon: <CollectionsBookmarkIcon sx={{ color: 'navy' }} />,
        title: 'Automatic Cyber Incident Collation',
        description:'Our tool effortlessly gathers cyber incident data from multiple sources (inc Marsh Data Uploaded), saving time and effort.',
    },
    {
        icon: <EqualizerIcon sx={{ color: 'navy' }} />,
        title: 'Cyber Trends Dashboard',
        description:'View Trends Internal Marsh & External Internet Data, extracting deeper insights quickly.',
    },
    {
        icon: <AccountTreeIcon sx={{ color: 'navy' }} />,
        title: 'Data & Slides Version Control',
        description: 'Keep track of Marsh Internal Data uploaded as well as slides generated.',
    }
];
  
  return (
    <Grid 
      container 
      component="main" 
      sx={{
        height: "100vh", // ensures that the bg takes full viewport height
        backgroundImage: `url(${bgImage})`,
        backgroundRepeat: "no-repeat",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
        position: 'relative',
        alignItems: 'center', 
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(212, 212, 212, 0.71)',
          backdropFilter: 'blur(1px)',
        }
      }}
    >
        
        {/* Left Side - Explanation of Tool itself */}
        <Grid item
        xs={false}
        sm={4}
        md={6}
        sx={{
            display: { xs: 'none', sm: 'flex' },
            alignItems: 'center',
            justifyContent: 'center', 
            position: 'relative'
        }}
        >
            <Stack sx={{ flexDirection: 'column', alignSelf: 'center', gap: 1.3, padding: 9 }}>
                <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
                    <Typography gutterBottom sx={{ fontWeight: 'medium', color: 'navy', fontSize: 30 }}>
                        MarshxNUS Cyber Content Tool
                    </Typography>
                </Box>
                {items.map((item, index) => (
                    <Stack key={index} direction="row" sx={{ gap: 2 }}>
                    {item.icon}
                    <div>
                        <Typography gutterBottom sx={{ fontWeight: 'medium' }}>
                            {item.title}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white' }}>
                            {item.description}
                        </Typography>
                    </div>
                    </Stack>
                ))}
            </Stack>
        </Grid>     
      
      {/* Right Side - Sign In Form */}
        <Grid item
            xs={12}
            sm={8}
            md={6}
            sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            padding: { xs: 2, sm: 3 },
            }}
        >
            <Paper elevation={6} sx={{
                width: '120%',
                maxWidth: 450,
                borderRadius: 2,
            }}>
                <Box
                    sx={{
                    py: 1,
                    px: 2,
                    backgroundImage: `url(${MarshLogoImage})`,
                    backgroundSize: 250,
                    backgroundRepeat: 'no-repeat',
                    backgroundPosition: 'center',
                    height: 65,
                    }}
                />
                <Box
                    sx={{
                    py: 2,
                    px: 2,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    }}
                >
                    <Typography component="h1" variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
                        Welcome Back!
                    </Typography>

                    <Box
                        component="form"
                        noValidate
                        onSubmit={handleLogin}
                        sx={{ width: '100%' }}
                    >
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="email"
                            label="Email Address"
                            name="email"
                            autoFocus
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="password"
                            label="Password"
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, 
                                mb: 2, 
                                color: 'white', 
                                backgroundColor: 'darkblue', 
                                fontSize: 16,
                                '&:hover': { backgroundColor: 'lightblue', color: 'darkblue'} 
                            }}>
                            Sign In
                        </Button>

                        {modal && (
                            <Typography
                            color="error"
                            variant="body2"
                            sx={{ mt: 2, textAlign: "center" }}
                            >
                            {errorMess}
                            </Typography>
                        )}
                    </Box>
                </Box>

            </Paper>
        </Grid>
    </Grid>
  );
}