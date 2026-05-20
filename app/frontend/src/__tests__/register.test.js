import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Register from "../pages/register";
import { apiCall } from "../lib/api";
import { useRouter } from "next/router";

jest.mock("../lib/api");

let pushMock;
beforeEach(() => {
  jest.clearAllMocks();
  pushMock = jest.fn();
  useRouter.mockImplementation(() => ({ push: pushMock }));
});

describe("Register Page", () => {
  it("renders all required fields (name, surname, email, ID, password, role, register button)", () => {
    render(<Register />);
    expect(screen.getByPlaceholderText("Name")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Surname")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("ID/Passport Number"),
    ).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Password")).toBeInTheDocument();
    expect(screen.getByLabelText("Role")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /register now/i }),
    ).toBeInTheDocument();
  });

  it('does NOT show licence number field when role is "User"', () => {
    render(<Register />);
    expect(
      screen.queryByPlaceholderText("Licence number"),
    ).not.toBeInTheDocument();
  });

  it('shows licence number field when role is changed to "Firefighter"', () => {
    render(<Register />);
    const roleSelect = screen.getByLabelText("Role");
    fireEvent.change(roleSelect, { target: { value: "Firefighter" } });
    expect(screen.getByPlaceholderText("Licence number")).toBeInTheDocument();
  });

  it("submits registration with correct data (User role)", async () => {
    apiCall.mockResolvedValueOnce({ message: "User created successfully" });
    render(<Register />);
    fireEvent.change(screen.getByPlaceholderText("Name"), {
      target: { value: "John" },
    });
    fireEvent.change(screen.getByPlaceholderText("Surname"), {
      target: { value: "Doe" },
    });
    fireEvent.change(screen.getByPlaceholderText("Email"), {
      target: { value: "john@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("ID/Passport Number"), {
      target: { value: "12345678" },
    });
    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "Secret123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /register now/i }));
    await waitFor(() => {
      expect(apiCall).toHaveBeenCalledWith("/api/register", "POST", {
        email: "john@example.com",
        password: "Secret123",
        name: "John",
        surname: "Doe",
        id_number: "12345678",
        licence_number: null,
        role: "User",
      });
      expect(pushMock).toHaveBeenCalledWith("/login?registered=true");
    });
  });

  it("submits registration with licence number when Firefighter role is selected", async () => {
    apiCall.mockResolvedValueOnce({ message: "User created successfully" });
    render(<Register />);
    fireEvent.change(screen.getByPlaceholderText("Name"), {
      target: { value: "Jane" },
    });
    fireEvent.change(screen.getByPlaceholderText("Surname"), {
      target: { value: "Firefighter" },
    });
    fireEvent.change(screen.getByPlaceholderText("Email"), {
      target: { value: "jane@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("ID/Passport Number"), {
      target: { value: "87654321" },
    });
    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "Fire123" },
    });
    const roleSelect = screen.getByLabelText("Role");
    fireEvent.change(roleSelect, { target: { value: "Firefighter" } });
    fireEvent.change(screen.getByPlaceholderText("Licence number"), {
      target: { value: "LIC-12345" },
    });
    fireEvent.click(screen.getByRole("button", { name: /register now/i }));
    await waitFor(() => {
      expect(apiCall).toHaveBeenCalledWith("/api/register", "POST", {
        email: "jane@example.com",
        password: "Fire123",
        name: "Jane",
        surname: "Firefighter",
        id_number: "87654321",
        licence_number: "LIC-12345",
        role: "Firefighter",
      });
      expect(pushMock).toHaveBeenCalledWith("/login?registered=true");
    });
  });

  it("shows error message when registration fails", async () => {
    apiCall.mockRejectedValueOnce(new Error("Email already registered"));
    render(<Register />);
    fireEvent.change(screen.getByPlaceholderText("Name"), {
      target: { value: "Test" },
    });
    fireEvent.change(screen.getByPlaceholderText("Surname"), {
      target: { value: "User" },
    });
    fireEvent.change(screen.getByPlaceholderText("Email"), {
      target: { value: "duplicate@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("ID/Passport Number"), {
      target: { value: "12345" },
    });
    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "pass" },
    });
    fireEvent.click(screen.getByRole("button", { name: /register now/i }));
    await waitFor(() => {
      expect(screen.getByText(/email already registered/i)).toBeInTheDocument();
    });
  });
});
