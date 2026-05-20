import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Login from "../pages/login";
import { apiCall } from "../lib/api";
import { useRouter } from "next/router";

jest.mock("../lib/api");

let pushMock;
beforeEach(() => {
  jest.clearAllMocks();
  pushMock = jest.fn();
  useRouter.mockImplementation(() => ({ push: pushMock }));
});

describe("Login Page", () => {
  it("renders email and password inputs and buttons", () => {
    render(<Login />);
    expect(
      screen.getByPlaceholderText("example@something.co.za"),
    ).toBeInTheDocument();
    expect(screen.getByPlaceholderText("••••••••")).toBeInTheDocument();
    expect(screen.getByText(/login/i)).toBeInTheDocument();
    expect(screen.getByText(/register/i)).toBeInTheDocument();
    expect(screen.getByText(/sign in as guest/i)).toBeInTheDocument();
  });

  it("submits login with correct credentials", async () => {
    apiCall.mockResolvedValueOnce({ access_token: "fake-jwt" });
    render(<Login />);
    fireEvent.change(screen.getByPlaceholderText("example@something.co.za"), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("••••••••"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByText(/login/i));

    await waitFor(() => {
      expect(apiCall).toHaveBeenCalledWith("/api/login", "POST", {
        email: "test@example.com",
        password: "password123",
      });
    });
  });

  it("stores token and redirects on success", async () => {
    apiCall.mockResolvedValueOnce({ access_token: "real-token" });
    render(<Login />);
    fireEvent.change(screen.getByPlaceholderText("example@something.co.za"), {
      target: { value: "a@b.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("••••••••"), {
      target: { value: "pass" },
    });
    fireEvent.click(screen.getByText(/login/i));

    await waitFor(() => {
      expect(localStorage.setItem).toHaveBeenCalledWith("token", "real-token");
      expect(pushMock).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("redirects to 2FA when required", async () => {
    apiCall.mockResolvedValueOnce({
      message: "2FA required",
      email: "user@example.com",
    });
    render(<Login />);
    fireEvent.change(screen.getByPlaceholderText("example@something.co.za"), {
      target: { value: "user@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("••••••••"), {
      target: { value: "pass" },
    });
    fireEvent.click(screen.getByText(/login/i));
    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith(
        "/verify-2fa?email=user%40example.com",
      );
    });
  });

  it("shows error on failed login", async () => {
    apiCall.mockRejectedValueOnce(new Error("Invalid credentials"));
    render(<Login />);
    fireEvent.change(screen.getByPlaceholderText("example@something.co.za"), {
      target: { value: "wrong@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("••••••••"), {
      target: { value: "wrong" },
    });
    fireEvent.click(screen.getByText(/login/i));
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});
