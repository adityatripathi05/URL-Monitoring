# Frontend Application for URL Shortener & Monitoring Service

## Overview

This frontend application provides the user interface for interacting with the URL Shortener & Monitoring service. Users can register, log in, shorten URLs, view their shortened URLs, and (eventually) monitor their performance. It is built as a single-page application (SPA) using React.

## Tech Stack

- **React:** A JavaScript library for building user interfaces.
- **React Router DOM:** For client-side routing and navigation.
- **Axios:** A promise-based HTTP client for making API requests to the backend.
- **JavaScript (ES6+):** The primary programming language.
- **HTML5 & CSS3:** For structuring and styling the application.
- **Nginx:** Used as the web server in the Dockerized deployment to serve static files.

## Project Structure

The `frontend/src` directory is organized as follows:

- **`src/assets/`**: Contains static assets like images, fonts, etc.
- **`src/components/`**: Holds reusable UI components that are used across multiple pages (e.g., `ProtectedRoute.js`).
- **`src/config/`**: For application-level configuration files (e.g., API base URLs, feature flags - currently placeholder).
- **`src/contexts/`**: Contains React Context API providers for global state management (e.g., `AuthContext.js` for authentication state).
- **`src/pages/`**: Top-level components that represent different pages of the application (e.g., `LoginPage.js`, `HomePage.js`).
- **`src/services/`**: Houses modules responsible for external interactions, primarily API calls (e.g., `apiService.js` which configures an Axios instance and handles token refresh).
- **`src/styles/`**: Includes global stylesheets or theme files (e.g., `global.css`).
- **`App.js`**: The main application component, responsible for setting up routing.
- **`index.js`**: The entry point of the React application, renders the root component and imports global styles.

## Available Scripts

In the `frontend` directory, you can run the following scripts:

-   **`npm start`**:
    Runs the app in development mode. Open [http://localhost:3000](http://localhost:3000) (or the port specified by `create-react-app`) to view it in your browser. The page will reload when you make changes.

-   **`npm test`**:
    Launches the test runner in interactive watch mode.

-   **`npm run build`**:
    Builds the app for production to the `build` folder. It correctly bundles React in production mode and optimizes the build for the best performance.

## Key Features Implemented

-   **User Authentication:**
    -   Login functionality.
    -   Secure token storage (`access_token`, `refresh_token` in `localStorage`).
    -   Automatic token refresh mechanism.
    -   Logout functionality.
-   **Protected Routes:** Ensures that certain parts of the application are accessible only to authenticated users.
-   **API Communication Layer:** A dedicated service (`apiService.js`) for managing API requests, including automatic attachment of authentication tokens and token refresh logic.

## Design Philosophy

-   **Modularity:** Components, services, and contexts are designed to be self-contained and reusable where possible, promoting maintainability.
-   **Scalability:** The project structure (separating pages, components, services, contexts) is intended to make it easier to add new features and scale the application.
-   **State Management:** Global authentication state is managed using the React Context API via `AuthContext.js`. This context provides authentication status, user information, and methods for login/logout. Local component state is managed using React hooks (`useState`, `useEffect`).

## Running the Frontend

### Development Mode (Standalone)

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm start
    ```
    The application will typically be available at `http://localhost:3000`.

### Using Docker (as part of the larger application)

The frontend is designed to be run as a service within the Dockerized application defined in the main `docker-compose.template.yml` (or `docker-compose.yml` generated from it).

1.  Ensure Docker and Docker Compose are installed.
2.  From the root of the project, run:
    ```bash
    docker-compose up -d url-frontend
    ```
    Or, to run all services:
    ```bash
    docker-compose up -d
    ```
3.  The frontend service (`url-frontend`) is configured to be accessible at **`http://localhost:3000`** on your host machine, as it maps port 3000 on the host to port 80 (Nginx) in the container.

## API Interaction

-   The frontend communicates with the backend API using `axios`, configured in `src/services/apiService.js`. This service includes an `apiClient` instance that automatically:
    -   Adds the JWT `access_token` to the `Authorization` header of requests.
    -   Handles automatic refresh of the `access_token` using the `refresh_token` when a 401 (Unauthorized) response is received.
-   Authentication tokens (JWT `access_token` and `refresh_token`) are received from the backend upon successful login and stored in `localStorage`. The `refreshToken` is used to obtain a new `access_token` without requiring the user to log in again.

## Future Enhancements (Optional)

-   **UI Library Integration:** Incorporate a UI component library (e.g., Material-UI, Ant Design) for a more polished and consistent look and feel.
-   **Advanced State Management:** For more complex global state, consider libraries like Redux Toolkit or Zustand.
-   **Internationalization (i18n):** Add support for multiple languages.
-   **Comprehensive Unit and Integration Tests:** Expand test coverage using Jest and React Testing Library.
-   **URL Management Features:** Implement UI for creating, listing, editing, and deleting shortened URLs.
-   **Dashboard and Analytics:** Develop a dashboard to display analytics for shortened URLs.

This README provides a comprehensive guide to the frontend application.
