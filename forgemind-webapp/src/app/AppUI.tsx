import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import BottomBar from "./components/BottomBar";
import ConfirmationModal from "./components/ConfirmationModal";
import { sendPrompt, getUserChats, getChatMessages, deleteChat, checkPluginLoginStatus } from "./api";
import Header from "../components/layout/Header";
import { supabase } from "../supabaseClient";
import { useNavigate, useLocation } from "react-router-dom";

// Import modular CSS
import "./styles/reset.css";
import "./styles/layout.css";
import "./styles/ChatWindow.css";
import "./styles/BottomBar.css";
import "./styles/Sidebar.css";

import fullLogo from "./assets/full_logo.png";
import logoIcon from "./assets/logo_icon.png";
import { Chat, Message } from "./types";

interface AppProps {
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
  initialChatId?: string;
}

const AppUI: React.FC<AppProps> = ({ onToggleSidebar, sidebarOpen, initialChatId }) => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatIndex, setActiveChatIndex] = useState(-1);
  const [userId, setUserId] = useState<string | null>(null);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isInitializing, setIsInitializing] = useState<boolean>(true);
  const [initializingWithChatId, setInitializingWithChatId] = useState<boolean>(!!initialChatId);
  const [creatingNewChat, setCreatingNewChat] = useState<boolean>(false);
  const [isNavigating, setIsNavigating] = useState<boolean>(false);
  const navigate = useNavigate();
  const location = useLocation();

  // State for delete confirmation modal
  const [deleteModalOpen, setDeleteModalOpen] = useState<boolean>(false);
  const [chatToDelete, setChatToDelete] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Effect to track if we're initializing with a chat ID
  useEffect(() => {
    if (initialChatId) {
      setInitializingWithChatId(true);
    }
  }, [initialChatId]);

  // Get the user ID on component mount
  useEffect(() => {
    const getCurrentUser = async () => {
      try {
        const { data } = await supabase.auth.getUser();
        const currentUserId = data.user?.id || null;
        setUserId(currentUserId);

        // If user is logged in, load their chats but don't activate any yet
        if (currentUserId) {
          await loadUserChats(currentUserId);
        } else {
          // Mark initialization as complete if no user is found
          setIsInitializing(false);
          setInitializingWithChatId(false);
        }
      } catch (error) {
        console.error("Error getting current user:", error);
        setIsInitializing(false);
        setInitializingWithChatId(false);
      }
    };

    getCurrentUser();

    // Set up listener for auth state changes - but only for sign-out
    // This prevents multiple refreshes on sign-in
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      console.log(`Auth event: ${event}`);

      // For sign-out, reset the app state
      if (event === 'SIGNED_OUT') {
        setUserId(null);
        setChats([]);
        setActiveChatIndex(-1);
        setIsInitializing(false);
        setInitializingWithChatId(false);
        // Reset URL to dashboard without a specific chat - but only if we're not initializing
        navigate('/dashboard');
      }

      // We handle SIGNED_IN in the initial getCurrentUser call to avoid duplicates
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [navigate]);

  // Effect to handle initialChatId from URL when component mounts or when chats are loaded
  useEffect(() => {
    if (initialChatId && chats.length > 0 && !isInitializing) {
      // Find the chat index for the given chat ID
      const chatIndex = chats.findIndex(chat => chat.id === initialChatId);

      // If the chat exists in our loaded chats, set it as active
      if (chatIndex !== -1) {
        setActiveChatIndex(chatIndex);
        setInitializingWithChatId(false);
      } else if (initialChatId.startsWith('temp-')) {
        // If it's a temporary ID that we can't find, it might be 
        // because we just navigated to it and the chat isn't in state yet
        // We'll leave the URL as is and not force a navigation away
        setInitializingWithChatId(false);
      } else {
        // If we couldn't find the chat and it's not a temporary ID,
        // go to new chat view
        setActiveChatIndex(-1);
        setInitializingWithChatId(false);
        // Navigate to dashboard since we couldn't find this chat
        navigate('/dashboard', { replace: true });
      }
    } else if (!initialChatId && !isInitializing) {
      // If there's no chat ID in the URL and we're done initializing,
      // make sure we're in new chat mode
      setInitializingWithChatId(false);
    }
  }, [initialChatId, chats, isInitializing, navigate]);

  // Function to load user chats from the database
  const loadUserChats = async (userId: string) => {
    try {
      const response = await getUserChats(userId);

      // Check for valid response structure
      if (!response || response.status !== 'success' || !response.chats) {
        console.error("Invalid response from getUserChats:", response);
        setIsInitializing(false);
        setInitializingWithChatId(false);
        return;
      }

      const userChats = response.chats;

      // Process each chat to load messages, but handle errors gracefully
      const processedChats: Chat[] = [];

      for (const chatInfo of userChats) {
        try {
          const messagesResponse = await getChatMessages(chatInfo.id);

          // Remove "Chat " prefix if it exists
          const chatName = chatInfo.title?.startsWith("Chat ")
            ? chatInfo.title.substring(5)
            : chatInfo.title || "Untitled Chat";

          // Create chat object for our state
          const chat: Chat = {
            id: chatInfo.id,
            name: chatInfo.title.replace(/^Chat /, '') || "Untitled Chat", // Remove "Chat " prefix
            messages: messagesResponse.messages,
            threadId: chatInfo.thread_id,
            updated_at: chatInfo.updated_at
          };

          processedChats.push(chat);
        } catch (error) {
          // Log the error but continue processing other chats
          console.error(`Error loading messages for chat ${chatInfo.id}:`, error);
          // Don't add this chat to the list
          processedChats.push({
            id: chatInfo.id,
            name: chatInfo.title.replace(/^Chat /, '') || "Untitled Chat", // Remove "Chat " prefix
            messages: [],
            error: true,
            threadId: chatInfo.thread_id,
            updated_at: chatInfo.updated_at
          });
        }
      }

      // Sort chats by updated_at (most recent first)
      processedChats.sort((a, b) => {
        // If Chat object has updated_at field, use it for sorting
        if (a.updated_at && b.updated_at) {
          // Convert timestamps to Date objects for comparison
          const dateA = new Date(a.updated_at);
          const dateB = new Date(b.updated_at);
          // Sort in descending order (newest first)
          return dateB.getTime() - dateA.getTime();
        }
        // Fallback to threadId comparison if no timestamps available
        return (b.threadId || '').localeCompare(a.threadId || '');
      });

      // Update state with the processed chats
      setChats(processedChats);

      // Mark initialization as complete
      setIsInitializing(false);
    } catch (error) {
      console.error("Error loading user chats:", error);
      // Still mark initialization as complete even if we encounter an error
      setIsInitializing(false);
      setInitializingWithChatId(false);
    }
  };

  // Create a new chat
  function handleNewChat() {
    // Show the empty UI without creating a new chat in the sidebar
    // Just set activeChatIndex to -1 to indicate we're in "new chat" mode
    setActiveChatIndex(-1);
    setInput("");
    // Close the sidebar
    if (sidebarOpen) {
      onToggleSidebar();
    }
    // Update URL to dashboard without a specific chat
    navigate('/dashboard');
  }

  // Use optional chaining to safely access messages
  const currentMessages = activeChatIndex >= 0 ? chats[activeChatIndex]?.messages || [] : [];

  // Handle sending from the BottomBar component
  const handleSend = () => {
    if (!input.trim() || isLoading) {
      return;
    }

    // Clear input field and set loading state
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    // Process the message
    onSend(currentInput);
  };

  const onSend = async (input: string) => {
    if (!input.trim()) return;

    setIsLoading(true);
    // Creating a new chat if we're not in an existing chat
    const isNewChat = activeChatIndex === -1;

    // If this is the first message in a chat, use it to set the chat name
    if (isNewChat) {
      // Truncate long inputs to a reasonable length for the chat name
      const chatName = input.length > 25 ? `${input.substring(0, 25)}...` : input;
      setInput("");
    } else {
      setInput("");
    }

    // Create user message object
    const userMessage: Message = {
      role: "user",
      content: input,
    };

    let updatedChats = [...chats];
    let newChatIndex = activeChatIndex;

    if (isNewChat) {
      // For new chats, create with user message only - no ID yet
      const newChat: Chat = {
        id: "", // We'll set this after API call returns
        name: input, // Use input as the name without "Chat " prefix
        messages: [userMessage], // Add the user message
        threadId: undefined,
        updated_at: new Date().toISOString() // Set current timestamp to ensure it sorts to the top
      };

      // Add the new chat to the beginning of the array (most recent first)
      updatedChats = [newChat, ...chats];
      // Set the index to the newly added chat (now at position 0)
      newChatIndex = 0;
    } else {
      // Adding message to existing chat
      updatedChats[activeChatIndex].messages.push(userMessage);
      // Update the timestamp
      updatedChats[activeChatIndex].updated_at = new Date().toISOString();

      // Re-sort the chats to ensure the active one moves to the top
      updatedChats.sort((a, b) => {
        if (a.updated_at && b.updated_at) {
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        }
        return 0;
      });

      // Find the new index of the active chat after sorting
      newChatIndex = updatedChats.findIndex(chat => chat.id === updatedChats[activeChatIndex].id);
    }

    // Update state to reflect the changes
    setChats(updatedChats);
    setActiveChatIndex(newChatIndex);

    try {
      // Check if userId is available before proceeding
      if (!userId) {
        throw new Error("User not authenticated. Please sign in.");
      }

      // Check if the plugin is connected before sending the prompt
      const pluginStatus = await checkPluginLoginStatus(userId);
      console.log("Plugin status before sending prompt:", pluginStatus);

      // If plugin is not connected, show an error message instead of sending the prompt
      if (!pluginStatus.is_connected || pluginStatus.is_logged_out) {
        // First update the state to show the user's message
        setInput("");

        // Create a copy of the current chats
        const updatedChats = [...chats];

        // Get the index of the active chat
        const chatIndex = newChatIndex;

        // Since we already added the user message above, don't add it again
        // Just add the error message about plugin status
        const errorMessage: Message = {
          role: "assistant" as const,
          content: "⚠️ Plugin is offline or disconnected. Please connect your Fusion 360 plugin and log in to use this feature."
        };

        // Add error message
        updatedChats[chatIndex].messages.push(errorMessage);

        // Update state
        setChats([...updatedChats]);

        return;
      }

      // First, send the prompt and get the initial response
      const currentThreadId = isNewChat ? undefined : updatedChats[newChatIndex].threadId;
      const aiResponse = await sendPrompt(input, userId, currentThreadId);

      // Update thread ID if available (OpenAI's thread ID)
      if (aiResponse.thread_id) {
        updatedChats[newChatIndex].threadId = aiResponse.thread_id;
      }

      // CRITICAL SECTION: Handle chat ID and navigation
      if (isNewChat && aiResponse.chat_id) {
        // Set the permanent chat ID (our database primary key)
        const permanentChatId = aiResponse.chat_id;
        updatedChats[newChatIndex].id = permanentChatId;

        // Remove the temporary messages
        // DO NOT add any system messages here

        // IMPROVED APPROACH: Update state before navigation
        setChats([...updatedChats]);

        // Set navigation state to indicate we're changing URL
        setIsNavigating(true);

        // Use React Router navigation without delay
        // This prevents full page reload while still updating the URL
        navigate(`/dashboard/${permanentChatId}`, { replace: true });
      }

      // Create AI message
      const aiMessage: Message = {
        role: "assistant",
        content: aiResponse.response,
      };

      // Add AI message to chat
      updatedChats[newChatIndex].messages.push(aiMessage);

      // Update the updated_at timestamp to ensure proper sorting
      updatedChats[newChatIndex].updated_at = new Date().toISOString();

      // Re-sort chats after updating
      updatedChats.sort((a, b) => {
        if (a.updated_at && b.updated_at) {
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        }
        return 0;
      });

      // Update state with the new message
      setChats([...updatedChats]);
      setIsNavigating(false); // Navigation complete

    } catch (error) {
      console.error("Error calling API:", error);

      // Create error message
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      };

      // Add error message to chat
      updatedChats[newChatIndex].messages.push(errorMessage);

      // Update state
      setChats([...updatedChats]);
    } finally {
      setIsLoading(false);
    }
  };

  // New Quick Tool Handlers
  const handleSuggestCAD = () => {
    console.log("Suggest a CAD Tool clicked");
    // Add your logic here
  };

  const handleCrashAnalysis = () => {
    console.log("Run Crash Analysis clicked");
    // Add your logic here
  };

  // Show confirmation modal before deleting
  function handleDeleteChat(index: number) {
    setChatToDelete(index);
    setDeleteModalOpen(true);
  }

  // Close the delete confirmation modal
  function cancelDelete() {
    setChatToDelete(null);
    setDeleteModalOpen(false);
  }

  // Confirm and perform chat deletion
  async function confirmDelete() {
    if (chatToDelete === null || isDeleting) return;

    setIsDeleting(true);

    try {
      const chatId = chats[chatToDelete].id;

      // Skip API call for temporary chats that aren't in the database yet
      if (chatId && !chatId.startsWith('temp-') && !chatId.startsWith('chat-') && userId) {
        // Call API to delete the chat from the database
        await deleteChat(chatId, userId);
      }

      // Create a copy of the chats array without the deleted chat
      const updatedChats = [...chats];
      updatedChats.splice(chatToDelete, 1);
      setChats(updatedChats);

      // If the active chat was deleted, set no active chat
      if (activeChatIndex === chatToDelete) {
        setActiveChatIndex(-1);
        navigate('/dashboard', { replace: true });
      }
      // If the deleted chat was before the active chat, adjust the active index
      else if (activeChatIndex > chatToDelete) {
        setActiveChatIndex(activeChatIndex - 1);
      }

    } catch (error) {
      console.error("Error deleting chat:", error);
      // Maybe show an error toast here
    } finally {
      // Close the modal and reset states
      setDeleteModalOpen(false);
      setChatToDelete(null);
      setIsDeleting(false);
    }
  }

  // These empty handlers are placeholders for the removed modals
  const handleOptimize = () => console.log("Optimize feature removed");
  const handleRefine = () => console.log("Refine feature removed");
  const handleRelations = () => console.log("Relations feature removed");

  // Loading indicator for entire chat area
  const renderLoadingScreen = () => {
    return (
      <div className="loading-screen">
        <div className="spinner-container">
          <div className="spinner"></div>
          <p>Loading your chat...</p>
        </div>
      </div>
    );
  };

  // Effect to prevent auto-refreshes
  useEffect(() => {
    // Flag to track if the component is mounted
    let isMounted = true;

    // Cleanup function to run when component unmounts
    return () => {
      isMounted = false;
    };
  }, []);

  // Effect to detect and prevent unwanted navigation resets
  useEffect(() => {
    // Store the current location when it changes
    const currentPath = location.pathname;
    console.log("Location changed to:", currentPath);

    // Cleanup function
    return () => {
      console.log("Location changing from:", currentPath);
    };
  }, [location.pathname]);

  // Add a navigation effect to track URL changes
  useEffect(() => {
    // When location changes, set isNavigating to false
    setIsNavigating(false);
  }, [location.pathname]);

  // Effect to close the sidebar when the user clicks away
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const sidebarElement = document.querySelector('.sidebar');
      if (sidebarOpen && sidebarElement && !sidebarElement.contains(event.target as Node)) {
        onToggleSidebar();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [sidebarOpen, onToggleSidebar]);

  // Function to handle chat selection
  const handleChatSelection = (index: number) => {
    // Only navigate if actually changing chats
    if (index !== activeChatIndex) {
      console.log(`Selecting chat at index ${index}, chat ID: ${chats[index]?.id}`);
      setActiveChatIndex(index);

      // Update URL based on selected chat
      if (index >= 0 && chats[index]?.id) {
        const chatId = chats[index]?.id;

        // Only navigate if we have a permanent chat ID (not a temporary one)
        if (chatId && !chatId.startsWith('temp-')) {
          // Compare current path with target path to avoid redundant navigation
          const currentPath = location.pathname;
          const targetPath = `/dashboard/${chatId}`;

          console.log(`Navigation check: current=${currentPath}, target=${targetPath}`);

          if (!currentPath.endsWith(chatId)) {
            console.log(`Navigating to ${targetPath}`);
            navigate(targetPath, { replace: true });
          } else {
            console.log(`Already at the correct path, no navigation needed`);
          }
        } else {
          // If it's a temporary ID, just stay on dashboard
          console.log(`Chat has temporary ID (${chatId}), staying on dashboard`);

          // Only navigate if we're not already on the dashboard
          if (location.pathname !== '/dashboard') {
            navigate('/dashboard', { replace: true });
          }
        }
      } else if (index === -1 && location.pathname !== '/dashboard') {
        // If selecting "new chat", navigate to dashboard
        console.log(`Navigating to dashboard for new chat`);
        navigate('/dashboard', { replace: true });
      }
    } else {
      console.log(`Already on chat at index ${index}, no change`);
    }
  };

  return (
    <div className="app-wrapper">
      <Header onToggleSidebar={onToggleSidebar} />

      <div className={sidebarOpen ? "app-container sidebar-open" : "app-container"}>
        <div className={sidebarOpen ? "sidebar" : "sidebar closed"}>
          <Sidebar
            chats={chats}
            activeChatIndex={activeChatIndex}
            setActiveChatIndex={handleChatSelection}
            onNewChat={handleNewChat}
            onDeleteChat={handleDeleteChat}
            onOptimize={handleOptimize}
            onRefine={handleRefine}
            onRelations={handleRelations}
            onSuggestCAD={handleSuggestCAD}
            onCrashAnalysis={handleCrashAnalysis}
            isLoading={isLoading}
          />
        </div>

        {/* Show loading screen while initializing with a chat ID */}
        {initializingWithChatId ? (
          renderLoadingScreen()
        ) : (
          <ChatWindow
            chats={chats}
            activeChatIndex={activeChatIndex}
            isLoading={isLoading || isInitializing}
            fullLogo={fullLogo}
            isNavigating={isNavigating}
          />
        )}

        <BottomBar
          input={input}
          setInput={setInput}
          onSend={handleSend}
          logoIcon={logoIcon}
          className={activeChatIndex === -1 || (activeChatIndex >= 0 && chats[activeChatIndex]?.messages?.length === 0) ? "centered-bottom-bar" : ""}
        />

        {/* Confirmation Modal for Deleting Chats */}
        <ConfirmationModal
          isOpen={deleteModalOpen}
          title="Delete Chat"
          message="Are you sure you want to delete this chat? This action cannot be undone."
          confirmButtonText={isDeleting ? "Deleting..." : "Delete"}
          cancelButtonText="Cancel"
          onConfirm={confirmDelete}
          onCancel={cancelDelete}
        />
      </div>
    </div>
  );
};

export default AppUI;
