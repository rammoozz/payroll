describe('Payroll Run Flow', () => {
  beforeEach(() => {
    // Login first
    cy.clearLocalStorage();
    cy.visit('/login');
    cy.get('[data-cy=email]').type('smith@demo.com');
    cy.get('[data-cy=password]').type('demo123');
    cy.get('[data-cy=submit]').click();
    
    // Wait for redirect to employees page
    cy.url().should('include', '/employees');
  });

  it('runs payroll and shows progress', () => {
    // Should see employees
    cy.contains('Smith Family Office');
    cy.contains('John Butler');
    cy.contains('Mary Chef');
    
    // Click run payroll button
    cy.get('[data-cy=run-payroll]').click();
    
    // Should redirect to payroll status page
    cy.url().should('match', /\/payroll\/\d+/);
    
    // Should show payroll run status
    cy.contains('Payroll Run #');
    cy.contains('Status:');
    
    // Should show progress (either PENDING or PROCESSING)
    cy.contains(/PENDING|PROCESSING/);
    
    // Wait for completion (with timeout)
    cy.contains('COMPLETED', { timeout: 30000 });
    
    // Download button should appear
    cy.get('[data-cy=download]').should('be.visible');
    
    // Can navigate back to employees
    cy.contains('Back to Employees').click();
    cy.url().should('include', '/employees');
  });

  it('handles logout correctly', () => {
    // Click logout
    cy.contains('Logout').click();
    
    // Should redirect to login
    cy.url().should('include', '/login');
    
    // Should clear auth data
    cy.window().then((win) => {
      expect(win.localStorage.getItem('token')).to.be.null;
      expect(win.localStorage.getItem('familyOfficeName')).to.be.null;
    });
    
    // Should not be able to access protected routes
    cy.visit('/employees');
    cy.url().should('include', '/login');
  });

  it('shows correct employee data for different family offices', () => {
    // Logout first
    cy.contains('Logout').click();
    
    // Login as Jones family
    cy.get('[data-cy=email]').type('jones@demo.com');
    cy.get('[data-cy=password]').type('demo123');
    cy.get('[data-cy=submit]').click();
    
    // Should see Jones Family Office
    cy.contains('Jones Family Office');
    
    // Should NOT see Smith employees
    cy.contains('John Butler').should('not.exist');
    cy.contains('Mary Chef').should('not.exist');
    
    // Should see Jones employees
    cy.contains('Emily Assistant');
    cy.contains('Michael Security');
  });
});