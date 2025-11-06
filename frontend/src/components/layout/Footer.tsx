import { Link } from 'react-router-dom';
import { Github, Twitter, Linkedin } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="border-t border-border bg-surface/50">
      <div className="container-custom py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="text-2xl font-bold">
              <span className="text-text-primary">Track</span>
              <span className="gradient-text">ly</span>
            </div>
            <p className="text-text-secondary text-sm">
              Streamline your job and scholarship applications with AI-powered automation.
            </p>
            <div className="flex space-x-4">
              <SocialLink href="https://github.com" icon={Github} />
              <SocialLink href="https://twitter.com" icon={Twitter} />
              <SocialLink href="https://linkedin.com" icon={Linkedin} />
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="font-semibold text-text-primary mb-4">Product</h3>
            <ul className="space-y-2">
              <FooterLink to="/features">Features</FooterLink>
              <FooterLink to="/pricing">Pricing</FooterLink>
              <FooterLink to="/roadmap">Roadmap</FooterLink>
              <FooterLink to="/changelog">Changelog</FooterLink>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="font-semibold text-text-primary mb-4">Company</h3>
            <ul className="space-y-2">
              <FooterLink to="/about">About</FooterLink>
              <FooterLink to="/blog">Blog</FooterLink>
              <FooterLink to="/careers">Careers</FooterLink>
              <FooterLink to="/contact">Contact</FooterLink>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="font-semibold text-text-primary mb-4">Legal</h3>
            <ul className="space-y-2">
              <FooterLink to="/privacy">Privacy Policy</FooterLink>
              <FooterLink to="/terms">Terms of Service</FooterLink>
              <FooterLink to="/cookies">Cookie Policy</FooterLink>
              <FooterLink to="/security">Security</FooterLink>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-border text-center text-text-secondary text-sm">
          <p>&copy; {new Date().getFullYear()} Trackly. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

const FooterLink = ({ to, children }: { to: string; children: React.ReactNode }) => (
  <li>
    <Link
      to={to}
      className="text-text-secondary hover:text-accent transition-colors duration-200 text-sm"
    >
      {children}
    </Link>
  </li>
);

const SocialLink = ({ href, icon: Icon }: { href: string; icon: any }) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className="text-text-secondary hover:text-accent transition-colors duration-200"
  >
    <Icon size={20} />
  </a>
);
