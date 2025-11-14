import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  CircularProgress,
  Avatar,
  Fade,
  Chip,
  Link,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import AttachFileIcon from "@mui/icons-material/AttachFile";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import PersonIcon from "@mui/icons-material/Person";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";

// Type for a single message
interface Message {
  sender: "user" | "bot";
  text: string;
  source: string;
  paragraph: string;
  webViewLink: string;
  document_name : string;
}

export default function ChatApp() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Send query to backend
  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      sender: "user",
      text: input,
      source: "",
      paragraph: "",
      webViewLink: "",
      document_name : ""
    };
    const formData = new FormData();
    formData.append("query", input);

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/query/", {
        method: "POST",
        body: formData,
      });
      const data: {
        response?: string;
        source?: string;
        paragraph?: string;
        webViewLink?: string;
        doc_name?:string;
      } = await response.json();

      const botMessage: Message = {
        sender: "bot",
        text: data.response || "No response",
        source: data.source || "",
        paragraph: data.paragraph || "",
        webViewLink: data.webViewLink || "",
        document_name : data.doc_name || ""
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Error connecting to server",
          source: "",
          paragraph: "",
          webViewLink: "",
          document_name  : ""
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Upload file
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;

    const formData = new FormData();
    formData.append("file", uploadedFile);

    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text: `Uploaded: ${uploadedFile.name}`,
        source: "",
        paragraph: "",
        webViewLink: "",
        document_name : "",
      },
    ]);

    try {
      const res = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });

      const data: {
        message?: string;
        source?: string;
        paragraph?: string;
        webViewLink?: string;
        doc_name?:string;
      } = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: data.message || "File processed successfully!",
          source: data.source || "",
          paragraph: data.paragraph || "",
          webViewLink: data.webViewLink || "",
          document_name : data.doc_name || "",
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "File upload failed.",
          source: "",
          paragraph: "",
          webViewLink: "",
          document_name : ""
        },
      ]);
    }
  };

  return (
    <Box
      sx={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        p: 2,
      }}
    >
      <Paper
        elevation={24}
        sx={{
          width: "100%",
          maxWidth: 800,
          height: "90vh",
          display: "flex",
          flexDirection: "column",
          borderRadius: 4,
          overflow: "hidden",
          background: "rgba(255, 255, 255, 0.95)",
          backdropFilter: "blur(10px)",
        }}
      >
        {/* Header */}

        {/* Chat messages */}
        <Box
          sx={{
            flex: 1,
            overflowY: "auto",
            p: 3,
            background: "#f8f9fa",
            display: "flex",
            flexDirection: "column",
            gap: 2,
          }}
        >
          {messages.length === 0 && (
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                gap: 2,
                opacity: 0.6,
              }}
            >
              <SmartToyIcon sx={{ fontSize: 64, color: "#a4a4a4ff" }} />
              <Typography variant="h6" color="text.secondary">
                Start a conversation
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ask me anything or upload a file
              </Typography>
            </Box>
          )}

          {messages.map((msg, index) => (
            <Fade in={true} key={index} timeout={500}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent:
                    msg.sender === "user" ? "flex-end" : "flex-start",
                  gap: 1.5,
                  alignItems: "flex-start",
                }}
              >
                {msg.sender === "bot" && (
                  <Avatar
                    sx={{
                      bgcolor: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                      width: 36,
                      height: 36,
                    }}
                  >
                    <SmartToyIcon fontSize="small" />
                  </Avatar>
                )}

                <Box sx={{ maxWidth: "70%" }}>
                  <Paper
                    elevation={2}
                    sx={{
                      p: 2,
                      borderRadius: 3,
                      background:
                        msg.sender === "user"
                          ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                          : "white",
                      color: msg.sender === "user" ? "white" : "text.primary",
                      boxShadow:
                        msg.sender === "user"
                          ? "0 4px 12px rgba(102, 126, 234, 0.4)"
                          : "0 2px 8px rgba(0,0,0,0.08)",
                      borderTopRightRadius: msg.sender === "user" ? 4 : 16,
                      borderTopLeftRadius: msg.sender === "bot" ? 4 : 16,
                    }}
                  >
                    <Typography
                      variant="body1"
                      sx={{
                        wordBreak: "break-word",
                        lineHeight: 1.6,
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {msg.text}
                    </Typography>

                    {/* Source Information */}
                    {msg.document_name && (
                      <Box sx={{ mt: 2, pt: 1.5, borderTop: "1px solid rgba(0,0,0,0.1)" }}>
                        <Chip
                          icon={<InsertDriveFileIcon />}
                          label={msg.document_name}
                          size="small"
                          sx={{
                            mb: 1,
                            bgcolor: msg.sender === "user" ? "rgba(255,255,255,0.2)" : "rgba(102, 126, 234, 0.1)",
                            color: msg.sender === "user" ? "white" : "#667eea",
                          }}
                        />
                        {msg.paragraph && (
                          <Typography
                            variant="caption"
                            sx={{
                              display: "block",
                              opacity: 0.8,
                              fontStyle: "italic",
                              mb: 1,
                            }}
                          >
                            "{msg.paragraph}"
                          </Typography>
                        )}
                        {msg.webViewLink &&(
                          <Link
                            href={msg.webViewLink}
                            target="_blank"
                            rel="noopener"
                            sx={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: 0.5,
                              fontSize: "0.875rem",
                              color: msg.sender === "user" ? "white" : "#667eea",
                              textDecoration: "none",
                              "&:hover": { textDecoration: "underline" },
                            }}
                          >
                            View Source <OpenInNewIcon fontSize="inherit" />
                          </Link>
                        )}
                      </Box>
                    )}
                  </Paper>
                </Box>

                {msg.sender === "user" && (
                  <Avatar
                    sx={{
                      bgcolor: "#e0e0e0",
                      width: 36,
                      height: 36,
                    }}
                  >
                    <PersonIcon fontSize="small" />
                  </Avatar>
                )}
              </Box>
            </Fade>
          ))}

          {loading && (
            <Fade in={true}>
              <Box sx={{ display: "flex", gap: 1.5, alignItems: "center" }}>
                <Avatar
                  sx={{
                    bgcolor: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    width: 36,
                    height: 36,
                  }}
                >
                  <SmartToyIcon fontSize="small" />
                </Avatar>
                <Paper
                  elevation={2}
                  sx={{
                    p: 2,
                    borderRadius: 3,
                    borderTopLeftRadius: 4,
                    display: "flex",
                    alignItems: "center",
                    gap: 1.5,
                  }}
                >
                  <CircularProgress size={20} sx={{ color: "#667eea" }} />
                  <Typography variant="body2" color="text.secondary">
                    Thinking...
                  </Typography>
                </Paper>
              </Box>
            </Fade>
          )}
          <div ref={messagesEndRef} />
        </Box>

        {/* Input area */}
        <Box
          sx={{
            p: 2.5,
            bgcolor: "white",
            borderTop: "1px solid #e0e0e0",
            display: "flex",
            gap: 1.5,
            alignItems: "center",
          }}
        >
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={handleFileUpload}
          />
          <IconButton
            onClick={() => fileInputRef.current?.click()}
            sx={{
              bgcolor: "#f5f5f5",
              "&:hover": { bgcolor: "#e0e0e0" },
            }}
          >
            <AttachFileIcon />
          </IconButton>

          <TextField
            fullWidth
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            variant="outlined"
            multiline
            maxRows={4}
            sx={{
              "& .MuiOutlinedInput-root": {
                borderRadius: 3,
                bgcolor: "#f8f9fa",
                "&:hover": {
                  bgcolor: "#f0f0f0",
                },
                "&.Mui-focused": {
                  bgcolor: "white",
                },
              },
            }}
          />

          <IconButton
            onClick={handleSend}
            disabled={!input.trim()}
            sx={{
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
              "&:hover": {
                background: "linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)",
              },
              "&.Mui-disabled": {
                background: "#e0e0e0",
                color: "#9e9e9e",
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
}
