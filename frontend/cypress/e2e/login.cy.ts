describe('Login Flow', () => {
  beforeEach(() => {
    // Clear any existing auth
    cy.clearLocalStorage();
    cy.visit('/login');
  });

  it('logs in successfully with valid credentials', () => {
    // Check that we're on the login page
    cy.contains('Family Office Payroll');
    cy.contains('Demo accounts:');
    
    // Enter credentials
    cy.get('[data-cy=email]').type('smith@demo.com');
    cy.get('[data-cy=password]').type('demo123');
    
    // Submit form
    cy.get('[data-cy=submit]').click();
    
    // Should redirect to employees page
    cy.url().should('include', '/employees');
    
    // Should see employees list
    cy.contains('Smith Family Office');
    cy.contains('Employees');
    
    // Should have stored token
    cy.window().then((win) => {
      expect(win.localStorage.getItem('token')).to.exist;
      expect(win.localStorage.getItem('familyOfficeName')).to.equal('Smith Family Office Admin');
    });
  });

  it('shows error with invalid credentials', () => {
    // Intercept the login request
    cy.intercept('POST', '/api/login', {
      statusCode: 401,
      body: { detail: 'Incorrect email or password' }
    }).as('loginRequest');
    
    // Enter wrong credentials
    cy.get('[data-cy=email]').type('smith@demo.com');
    cy.get('[data-cy=password]').type('wrongpassword');
    
    // Submit form
    cy.get('[data-cy=submit]').click();
    
    // Wait for the API call
    cy.wait('@loginRequest');
    
    // Should still be on login page (not redirected)
    cy.url().should('include', '/login');
    
    // Should show error message
    cy.get('.error').should('be.visible').and('contain', 'Incorrect email or password');
  });

  it('redirects to login when not authenticated', () => {
    // Try to visit protected route
    cy.visit('/employees');
    
    // Should redirect to login
    cy.url().should('include', '/login');
  });
});