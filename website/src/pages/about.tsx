import type {ReactNode} from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';

import styles from './about.module.css';

export default function About(): ReactNode {
  const centroGeoLogo = useBaseUrl('img/CentroGeo-CMX_Logo-V.png');
  const omLogo = useBaseUrl('img/Logo-OM-resized.png');

  return (
    <Layout title="About" description="About Whistlerlib">
      <main className={styles.about}>
        <div className="container">
          <h1>About</h1>

          <div className={styles.affiliations}>
            <div className={styles.affiliationColumn}>
              <img
                src={centroGeoLogo}
                alt="CentroGeo"
                className={styles.affiliationLogo}
              />
              <h3>CentroGeo</h3>
              <p>
                Whistlerlib is developed at the{' '}
                <Link href="https://www.centrogeo.org.mx/">CentroGeo</Link>.
              </p>
            </div>

            <div className={styles.affiliationColumn}>
              <img
                src={omLogo}
                alt="Observatorio Metropolitano CentroGeo"
                className={styles.affiliationLogo}
              />
              <h3>Observatorio Metropolitano</h3>
              <p>
                Whistlerlib is a research and tech product of the{' '}
                <Link href="https://observatoriogeo.mx">
                  Observatorio Metropolitano CentroGeo
                </Link>.
              </p>
            </div>
          </div>

          <h2>Authors</h2>
          <p>
            Whistlerlib is co-authored by{' '}
            <strong>
              <Link href="https://albertogarob.mx/">
                Dr. Alberto García Robledo
              </Link>
            </strong>{' '}
            and <strong>Dra. Angelina Espejel Trujillo</strong>, both at{' '}
            <Link href="https://www.centrogeo.org.mx/">CentroGeo</Link>,
            under <Link href="https://secihti.mx">SECIHTI</Link>'s{' '}
            <em>Investigadores por México</em> program.
          </p>
          <p>
            Inquiries: Dr. Alberto García Robledo,{' '}
            <Link href="mailto:algarcia@centrogeo.edu.mx">
              algarcia@centrogeo.edu.mx
            </Link>
            .
          </p>
        </div>
      </main>
    </Layout>
  );
}
