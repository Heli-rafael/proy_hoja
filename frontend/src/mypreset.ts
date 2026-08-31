import { definePreset } from '@primeuix/themes';
import Aura from '@primeuix/themes/aura';

const MyPreset = definePreset(Aura, {

    // =========================================================
    // SEMANTIC
    // =========================================================
    semantic: {

        primary: {
            50: '{emerald.50}',
            100: '{emerald.100}',
            200: '{emerald.200}',
            300: '{emerald.300}',
            400: '{emerald.400}',
            500: '{emerald.500}',
            600: '{emerald.600}',
            700: '{emerald.700}',
            800: '{emerald.800}',
            900: '{emerald.900}',
            950: '{emerald.950}'
        },

        colorScheme: {

            // =====================================================
            // LIGHT
            // =====================================================
            light: {

                surface: {
                    0: '#ffffff',
                    50: '#fafafa',
                    100: '#f4f4f5',
                    200: '#e4e4e7',
                    300: '#d4d4d8',
                    400: '#a1a1aa',
                    500: '#71717a',
                    600: '#52525b',
                    700: '#3f3f46',
                    800: '#27272a',
                    900: '#18181b',
                    950: '#09090b'
                },

                formField: {
                    background: '#ffffff',
                    disabledBackground: '#f4f4f5',

                    filledBackground: '#ffffff',
                    filledHoverBackground: '#ffffff',

                    borderColor: '#d4d4d8',
                    hoverBorderColor: '#a1a1aa',
                    focusBorderColor: '{primary.color}',

                    color: '#18181b',
                    placeholderColor: '#71717a',

                    shadow: 'none'
                }

            },


            // =====================================================
            // DARK
            // =====================================================
            dark: {

                surface: {
                    0: '#ffffff',
                    50: '#fafafa',
                    100: '#f4f4f5',
                    200: '#e4e4e7',
                    300: '#d4d4d8',
                    400: '#a1a1aa',
                    500: '#71717a',
                    600: '#52525b',
                    700: '#3f3f46',
                    800: '#27272a',
                    900: '#18181b',
                    950: '#09090b'
                },

                formField: {

                    background: '#121212',

                    disabledBackground: '#0E0E0E',

                    filledBackground: '#121212',
                    filledHoverBackground: '#181818',

                    borderColor: '#303030',
                    hoverBorderColor: '#444444',

                    focusBorderColor: '{primary.color}',

                    color: '#FAFAFA',
                    placeholderColor: '#A1A1A1',

                    shadow: 'none'
                }

            }

        }

    },


    // =========================================================
    // COMPONENTS
    // =========================================================
    components: {

        button: {

            colorScheme: {

                dark: {

                    root: {

                        borderRadius: '20px',

                        primary: {
                            background: '#10B981',
                            hoverBackground: '#059669',
                            activeBackground: '#047857',

                            borderColor: '#10B981',
                            hoverBorderColor: '#059669',
                            activeBorderColor: '#047857',

                            color: '#FFFFFF',
                            hoverColor: '#FFFFFF',
                            activeColor: '#FFFFFF'
                        },

                        success: {
                            background: '#16A34A',
                            hoverBackground: '#15803D',
                            activeBackground: '#166534',

                            borderColor: '#16A34A',
                            hoverBorderColor: '#15803D',
                            activeBorderColor: '#166534',

                            color: '#FFFFFF',
                            hoverColor: '#FFFFFF',
                            activeColor: '#FFFFFF'
                        },

                        info: {
                            background: '#2563EB',
                            hoverBackground: '#1D4ED8',
                            activeBackground: '#1E40AF',

                            borderColor: '#2563EB',
                            hoverBorderColor: '#1D4ED8',
                            activeBorderColor: '#1E40AF',

                            color: '#FFFFFF',
                            hoverColor: '#FFFFFF',
                            activeColor: '#FFFFFF'
                        },

                        warn: {
                            background: '#F59E0B',
                            hoverBackground: '#D97706',
                            activeBackground: '#B45309',

                            borderColor: '#F59E0B',
                            hoverBorderColor: '#D97706',
                            activeBorderColor: '#B45309',

                            color: '#FFFFFF',
                            hoverColor: '#FFFFFF',
                            activeColor: '#FFFFFF'
                        },

                        danger: {
                            background: '#DC2626',
                            hoverBackground: '#B91C1C',
                            activeBackground: '#991B1B',

                            borderColor: '#DC2626',
                            hoverBorderColor: '#B91C1C',
                            activeBorderColor: '#991B1B',

                            color: '#FFFFFF',
                            hoverColor: '#FFFFFF',
                            activeColor: '#FFFFFF'
                        }

                    }

                },


                light: {

                    root: {

                        // Personalización de los botones en modo claro

                        borderRadius: '20px',
                        

                    }

                }

            }

        },



        // =========================================================
        // SELECT BUTTON
        // =========================================================
        selectbutton: {

            colorScheme: {

                dark: {

                    root: {
                        borderRadius: '10px',
                        invalidBorderColor: '#EF4444'
                    }

                },

                light: {

                    root: {
                        borderRadius: '10px',
                        invalidBorderColor: '#DC2626'
                    }

                }

            }

        },


        // =========================================================
        // DIALOG
        // =========================================================
        dialog: {

            colorScheme: {

                dark: {

                    root: {
                        background: '#121212',
                        borderColor: '#303030',
                        color: '#FAFAFA',
                        shadow: '0 20px 50px rgba(0, 0, 0, 0.5)'
                    }

                },

                light: {

                    root: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        color: '#18181B',
                        shadow: '0 20px 50px rgba(0, 0, 0, 0.15)'
                    }

                }

            }

        },


        // =========================================================
        // SELECT
        // =========================================================
        select: {

            colorScheme: {

                dark: {

                    root: {
                        background: '#121212',
                        borderColor: '#303030',
                        color: '#FAFAFA',

                        hoverBorderColor: '#444444',
                        focusBorderColor: '{primary.color}',

                        shadow: 'none'
                    },

                    overlay: {
                        background: '#121212',
                        borderColor: '#303030',
                        color: '#FAFAFA',
                        shadow: '0 15px 40px rgba(0, 0, 0, 0.45)'
                    },

                    option: {
                        color: '#FAFAFA',
                        focusBackground: '#181818',
                        focusColor: '#FFFFFF',

                        selectedBackground: '#123D2D',
                        selectedColor: '#FFFFFF',

                        selectedFocusBackground: '#18553C',
                        selectedFocusColor: '#FFFFFF'
                    }

                },

                light: {

                    root: {
                        background: '#FFFFFF',
                        borderColor: '#D4D4D8',
                        color: '#18181B',

                        hoverBorderColor: '#A1A1AA',
                        focusBorderColor: '{primary.color}',

                        shadow: 'none'
                    },

                    overlay: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        color: '#18181B',
                        shadow: '0 15px 40px rgba(0, 0, 0, 0.15)'
                    },

                    option: {
                        color: '#18181B',
                        focusBackground: '#F4F4F5',
                        focusColor: '#18181B',

                        selectedBackground: '#D1FAE5',
                        selectedColor: '#065F46',

                        selectedFocusBackground: '#A7F3D0',
                        selectedFocusColor: '#064E3B'
                    }

                }

            }

        },


        // =========================================================
        // MULTISELECT
        // =========================================================
        multiselect: {

            colorScheme: {

                dark: {

                    root: {
                        background: '#121212',
                        borderColor: '#303030',
                        color: '#FAFAFA',

                        hoverBorderColor: '#444444',
                        focusBorderColor: '{primary.color}',

                        shadow: 'none'
                    },

                    overlay: {
                        background: '#121212',
                        borderColor: '#303030',
                        color: '#FAFAFA'
                    }

                },

                light: {

                    root: {
                        background: '#FFFFFF',
                        borderColor: '#D4D4D8',
                        color: '#18181B',

                        hoverBorderColor: '#A1A1AA',
                        focusBorderColor: '{primary.color}',

                        shadow: 'none'
                    },

                    overlay: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        color: '#18181B'
                    }

                }

            }

        },


        // =========================================================
        // TEXTAREA
        // =========================================================
        textarea: {

            colorScheme: {

                dark: {

                    root: {
                        background: '#121212',
                        borderColor: '#303030',
                        color: '#FAFAFA',

                        hoverBorderColor: '#444444',
                        focusBorderColor: '{primary.color}',

                        shadow: 'none'
                    }

                },

                light: {

                    root: {
                        background: '#FFFFFF',
                        borderColor: '#D4D4D8',
                        color: '#18181B',

                        hoverBorderColor: '#A1A1AA',
                        focusBorderColor: '{primary.color}',

                        shadow: 'none'
                    }

                }

            }

        },


        // =========================================================
        // PASSWORD
        // =========================================================
        password: {

            colorScheme: {

                dark: {

                    meter: {
                        background: '#303030'
                    },

                    icon: {
                        color: '#A1A1AA'
                    },

                    overlay: {
                        background: '#121212',
                        borderColor: '#303030',
                        color: '#FAFAFA',
                        shadow: '0 15px 40px rgba(0, 0, 0, 0.45)'
                    },

                    strength: {
                        weakBackground: '#EF4444',
                        mediumBackground: '#F59E0B',
                        strongBackground: '#10B981'
                    }

                },

                light: {

                    meter: {
                        background: '#E4E4E7'
                    },

                    icon: {
                        color: '#71717A'
                    },

                    overlay: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        color: '#18181B',
                        shadow: '0 15px 40px rgba(0, 0, 0, 0.15)'
                    },

                    strength: {
                        weakBackground: '#DC2626',
                        mediumBackground: '#D97706',
                        strongBackground: '#059669'
                    }

                }

            }

        },


        // =========================================================
        // ACCORDION
        // =========================================================
        accordion: {

            colorScheme: {

                dark: {

                    root: {
                        transitionDuration: '200ms'
                    },

                    panel: {
                        borderWidth: '0',
                        borderColor: '#303030'
                    },

                    header: {
                        background: '#121212',
                        hoverBackground: '#181818',
                        activeBackground: '#121212',
                        activeHoverBackground: '#181818',

                        color: '#FAFAFA',
                        hoverColor: '#FFFFFF',
                        activeColor: '#FFFFFF',

                        padding: '1rem 1.25rem',

                        borderWidth: '1px',
                        borderColor: '#303030',
                        borderRadius: '14px',

                        fontWeight: '600'
                    },

                    content: {
                        background: '#121212',
                        color: '#FAFAFA',

                        borderWidth: '0 1px 1px 1px',
                        borderColor: '#303030',

                        padding: '1rem 1.25rem'
                    }

                },

                light: {

                    root: {
                        transitionDuration: '200ms'
                    },

                    panel: {
                        borderWidth: '0',
                        borderColor: '#E4E4E7'
                    },

                    header: {
                        background: '#FFFFFF',
                        hoverBackground: '#FAFAFA',
                        activeBackground: '#FFFFFF',
                        activeHoverBackground: '#FAFAFA',

                        color: '#18181B',
                        hoverColor: '#18181B',
                        activeColor: '#18181B',

                        padding: '1rem 1.25rem',

                        borderWidth: '1px',
                        borderColor: '#E4E4E7',
                        borderRadius: '14px',

                        fontWeight: '600'
                    },

                    content: {
                        background: '#FFFFFF',
                        color: '#18181B',

                        borderWidth: '0 1px 1px 1px',
                        borderColor: '#E4E4E7',

                        padding: '1rem 1.25rem'
                    }

                }

            }

        },


        // =========================================================
        // TOOLTIP
        // =========================================================
        tooltip: {

            colorScheme: {

                dark: {

                    root: {
                        background: '#121212',
                        color: '#FAFAFA',
                        borderRadius: '8px',
                        shadow: '0 6px 18px rgba(0, 0, 0, 0.35)'
                    }

                },

                light: {

                    root: {
                        background: '#FFFFFF',
                        color: '#18181B',
                        borderRadius: '8px',
                        shadow: '0 6px 18px rgba(0, 0, 0, 0.12)'
                    }

                }

            }

        },


        // =========================================================
        // DRAWER
        // =========================================================
        drawer: {

            colorScheme: {

                dark: {

                    root: {
                        background: '#121212',
                        borderColor: '#303030',
                        color: '#FAFAFA',
                        shadow: '0 20px 50px rgba(0, 0, 0, 0.5)'
                    }

                },

                light: {

                    root: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        color: '#18181B',
                        shadow: '0 20px 50px rgba(0, 0, 0, 0.15)'
                    }

                }

            }

        },


        // =========================================================
        // FILE UPLOAD
        // =========================================================
        fileupload: {

            colorScheme: {

                dark: {

                    root: {
                        background: '#121212',
                        borderColor: '#303030',
                        color: '#FAFAFA',
                        borderRadius: '14px'
                    },

                    header: {
                        background: '#121212',
                        borderColor: '#303030'
                    }

                },

                light: {

                    root: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        color: '#18181B',
                        borderRadius: '14px'
                    },

                    header: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7'
                    }

                }

            }

        },


        // =========================================================
        // POPOVER
        // =========================================================
        popover: {

            colorScheme: {

                dark: {

                    root: {
                        background: '#121212',
                        borderColor: '#303030',
                        color: '#FAFAFA',
                        borderRadius: '15px',
                        shadow: '0 15px 40px rgba(0, 0, 0, 0.45)'
                    },

                },

                light: {

                    root: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        color: '#18181B',
                        borderRadius: '15px',
                        shadow: '0 15px 40px rgba(0, 0, 0, 0.15)'
                    },

                }

            }

        },


        // =========================================================
        // MENU
        // =========================================================
        menu: {

            colorScheme: {

                dark: {

                    root: {
                        background: '#121212',
                        borderColor: '#303030',
                        color: '#FAFAFA',
                        borderRadius: '10px',
                        shadow: '0 15px 40px rgba(0, 0, 0, 0.45)',
                        transitionDuration: '200ms'
                    },

                    list: {
                        padding: '0.5rem',
                        gap: '0.25rem'
                    },

                    item: {
                        focusBackground: '#181818',
                        color: '#FAFAFA',
                        focusColor: '#FFFFFF',
                        padding: '0.75rem 1rem',
                        borderRadius: '8px',
                        gap: '0.5rem',

                        icon: {
                            color: '#A1A1A1',
                            focusColor: '#FFFFFF'
                        }
                    },

                    submenuLabel: {
                        padding: '0.75rem 1rem',
                        fontWeight: '600',
                        background: '#121212',
                        color: '#A1A1AA'
                    },

                    separator: {
                        borderColor: '#303030'
                    }

                },

                light: {

                    root: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        color: '#18181B',
                        borderRadius: '10px',
                        shadow: '0 15px 40px rgba(0, 0, 0, 0.15)',
                        transitionDuration: '200ms'
                    },

                    list: {
                        padding: '0.5rem',
                        gap: '0.25rem'
                    },

                    item: {
                        focusBackground: '#F4F4F5',
                        color: '#18181B',
                        focusColor: '#18181B',
                        padding: '0.75rem 1rem',
                        borderRadius: '8px',
                        gap: '0.5rem',

                        icon: {
                            color: '#71717A',
                            focusColor: '#18181B'
                        }
                    },

                    submenuLabel: {
                        padding: '0.75rem 1rem',
                        fontWeight: '600',
                        background: '#FFFFFF',
                        color: '#71717A'
                    },

                    separator: {
                        borderColor: '#E4E4E7'
                    }

                }

            }

        },


        // =========================================================
        // MEGA MENU
        // =========================================================
        megamenu: {

            colorScheme: {

                dark: {

                    root: {
                        background: '#121212',
                        borderColor: '#303030',
                        borderRadius: '10px'
                    }

                },

                light: {

                    root: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        borderRadius: '10px'
                    }

                }

            }

        },


        // =========================================================
        // MENUBAR
        // =========================================================
        menubar: {

            colorScheme: {

                dark: {

                    root: {
                        background: '#121212',
                        borderColor: '#303030',
                        borderRadius: '10px',
                        color: '#FAFAFA',
                        gap: '0.5rem',
                        padding: '0.5rem 0.75rem',
                        transitionDuration: '200ms'
                    },

                    baseItem: {
                        borderRadius: '8px',
                        padding: '0.75rem 1rem'
                    },

                    item: {
                        focusBackground: '#181818',
                        activeBackground: '#181818',

                        color: '#FAFAFA',
                        focusColor: '#FFFFFF',
                        activeColor: '#FFFFFF',

                        padding: '0.75rem 1rem',
                        borderRadius: '8px',
                        gap: '0.5rem',

                        icon: {
                            color: '#A1A1A1',
                            focusColor: '#FFFFFF',
                            activeColor: '#FFFFFF'
                        }
                    },

                    submenu: {
                        padding: '0.5rem',
                        gap: '0.25rem',

                        background: '#121212',
                        borderColor: '#303030',
                        borderRadius: '10px',

                        shadow: '0 15px 40px rgba(0, 0, 0, 0.45)',

                        mobileIndent: '1rem',

                        icon: {
                            size: '0.75rem',
                            color: '#A1A1A1',
                            focusColor: '#FFFFFF',
                            activeColor: '#FFFFFF'
                        }
                    },

                    separator: {
                        borderColor: '#303030'
                    },

                    mobileButton: {
                        borderRadius: '50%',
                        size: '2.5rem',

                        color: '#FAFAFA',
                        hoverColor: '#FFFFFF',
                        hoverBackground: '#181818',

                        focusRing: {
                            width: '0',
                            style: 'none',
                            color: 'transparent',
                            offset: '0',
                            shadow: 'none'
                        }
                    }

                },


                light: {

                    root: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        borderRadius: '10px',
                        color: '#18181B',
                        gap: '0.5rem',
                        padding: '0.5rem 0.75rem',
                        transitionDuration: '200ms'
                    },

                    baseItem: {
                        borderRadius: '8px',
                        padding: '0.75rem 1rem'
                    },

                    item: {
                        focusBackground: '#F4F4F5',
                        activeBackground: '#F4F4F5',

                        color: '#18181B',
                        focusColor: '#18181B',
                        activeColor: '#18181B',

                        padding: '0.75rem 1rem',
                        borderRadius: '8px',
                        gap: '0.5rem',

                        icon: {
                            color: '#71717A',
                            focusColor: '#18181B',
                            activeColor: '#18181B'
                        }
                    },

                    submenu: {
                        padding: '0.5rem',
                        gap: '0.25rem',

                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        borderRadius: '10px',

                        shadow: '0 15px 40px rgba(0, 0, 0, 0.15)',

                        mobileIndent: '1rem',

                        icon: {
                            size: '0.75rem',
                            color: '#71717A',
                            focusColor: '#18181B',
                            activeColor: '#18181B'
                        }
                    },

                    separator: {
                        borderColor: '#E4E4E7'
                    },

                    mobileButton: {
                        borderRadius: '50%',
                        size: '2.5rem',

                        color: '#18181B',
                        hoverColor: '#18181B',
                        hoverBackground: '#F4F4F5',

                        focusRing: {
                            width: '0',
                            style: 'none',
                            color: 'transparent',
                            offset: '0',
                            shadow: 'none'
                        }
                    }

                }

            }

        },
        // =========================================================
        // PANEL MENU
        // =========================================================
        panelmenu: {

            colorScheme: {

                dark: {

                    root: {
                        gap: '0.5rem',
                        transitionDuration: '200ms'
                    },

                    panel: {
                        background: '#121212',
                        borderColor: '#303030',
                        borderWidth: '1px',
                        color: '#FAFAFA',
                        padding: '0.25rem',
                        borderRadius: '10px',

                        first: {
                            borderWidth: '1px 1px 0 1px',
                            topBorderRadius: '10px'
                        },

                        last: {
                            borderWidth: '0 1px 1px 1px',
                            bottomBorderRadius: '10px'
                        }
                    },

                    item: {
                        focusBackground: '#181818',
                        color: '#FAFAFA',
                        focusColor: '#FFFFFF',
                        gap: '0.5rem',
                        padding: '0.75rem 1rem',
                        borderRadius: '8px',

                        icon: {
                            color: '#A1A1A1',
                            focusColor: '#FFFFFF'
                        }
                    },

                    submenu: {
                        indent: '1rem'
                    },

                    submenuIcon: {
                        color: '#A1A1A1',
                        focusColor: '#FFFFFF'
                    }

                },


                light: {

                    root: {
                        gap: '0.5rem',
                        transitionDuration: '200ms'
                    },

                    panel: {
                        background: '#FFFFFF',
                        borderColor: '#E4E4E7',
                        borderWidth: '1px',
                        color: '#18181B',
                        padding: '0.25rem',
                        borderRadius: '10px',

                        first: {
                            borderWidth: '1px 1px 0 1px',
                            topBorderRadius: '10px'
                        },

                        last: {
                            borderWidth: '0 1px 1px 1px',
                            bottomBorderRadius: '10px'
                        }
                    },

                    item: {
                        focusBackground: '#F4F4F5',
                        color: '#18181B',
                        focusColor: '#18181B',
                        gap: '0.5rem',
                        padding: '0.75rem 1rem',
                        borderRadius: '8px',

                        icon: {
                            color: '#71717A',
                            focusColor: '#18181B'
                        }
                    },

                    submenu: {
                        indent: '1rem'
                    },

                    submenuIcon: {
                        color: '#71717A',
                        focusColor: '#18181B'
                    }

                }

            }

        },

    }

});

export default MyPreset;