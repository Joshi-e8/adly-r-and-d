import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { LoginForm } from '../LoginForm';
import { BrowserRouter } from 'react-router-dom';

// Mock auth store
const loginMock = vi.fn();
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    login: loginMock,
    isLoading: false,
  }),
}));

describe('LoginForm', () => {
    beforeEach(() => {
        loginMock.mockClear();
    });

    it('renders login form correctly', () => {
        render(
            <BrowserRouter>
                <LoginForm />
            </BrowserRouter>
        );
        expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
    });

    it('submits form with valid data', async () => {
        const user = userEvent.setup();
        loginMock.mockResolvedValue({}); // Success

        render(
            <BrowserRouter>
                 <LoginForm onSuccess={() => {}} />
            </BrowserRouter>
        );

        await user.type(screen.getByLabelText(/Email Address/i), 'test@example.com');
        await user.type(screen.getByLabelText(/Password/i), 'password123');
        
        await user.click(screen.getByRole('button', { name: /Sign In/i }));

        await waitFor(() => {
            expect(loginMock).toHaveBeenCalledWith({
                email: 'test@example.com',
                password: 'password123',
            });
        });
    });

    it('shows validation error for invalid email', async () => {
        const user = userEvent.setup();
        render(
            <BrowserRouter>
                <LoginForm />
            </BrowserRouter>
        );

        await user.type(screen.getByLabelText(/Email Address/i), 'invalid-email');
        await user.click(screen.getByRole('button', { name: /Sign In/i }));

        await waitFor(() => {
             expect(screen.getByText(/Invalid email address/i)).toBeInTheDocument();
        });
        expect(loginMock).not.toHaveBeenCalled();
    });
});
