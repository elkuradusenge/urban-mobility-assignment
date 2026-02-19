(() => {
  const totalTrips = document.querySelector("#total-trips");
  const totalVendors = document.querySelector("#total-vendors");
  const totalPayments = document.querySelector("#total-payments");
  const recentTripsBody = document.querySelector("#recent-trips-body");

  if (!totalTrips || !totalVendors || !totalPayments) {
    return;
  }

  const resolveEndpointBase = () => {
    if (window.location.protocol !== "file:") return "";
    return "http://localhost:3000";
  };

  const requestApi = async (path) => {
    const endpoints = [];
    const primary = `${resolveEndpointBase()}${path}`;
    endpoints.push(primary);
    if (primary !== `http://localhost:3000${path}`) {
      endpoints.push(`http://localhost:3000${path}`);
    }

    let lastError;
    for (const url of endpoints) {
      try {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response;
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError || new Error("Unable to reach server");
  };

  const parseDataArray = (payload) => {
    if (Array.isArray(payload)) return payload;
    if (payload?.success && Array.isArray(payload.data)) return payload.data;
    if (Array.isArray(payload?.data)) return payload.data;
    throw new Error("Unexpected response format");
  };

  const fetchCollection = async (path) => {
    const response = await requestApi(path);
    const payload = await response.json();
    return parseDataArray(payload);
  };

  const resolveTripStatus = (trip) => {
    if (typeof trip?.status === "string" && trip.status.trim()) {
      return trip.status.trim();
    }

    if (!trip?.dropoff_datetime) return "Completed";

    const dropoff = new Date(trip.dropoff_datetime);
    if (Number.isNaN(dropoff.getTime())) return "Completed";
    return dropoff < new Date() ? "Completed" : "Scheduled";
  };

  const statusClass = (status) => {
    const normalized = String(status || "").toLowerCase();
    if (normalized === "completed") return "completed";
    if (normalized === "scheduled") return "scheduled";
    if (normalized === "in progress") return "progress";
    if (normalized === "cancelled") return "cancelled";
    return "scheduled";
  };

  const formatAmount = (amount) => {
    const numeric = Number(amount);
    if (Number.isNaN(numeric)) return "N/A";
    return `${numeric.toLocaleString()} RWF`;
  };

  const renderRecentTrips = (trips) => {
    if (!recentTripsBody) return;

    if (!trips.length) {
      recentTripsBody.innerHTML = `
        <tr>
          <td colspan="5">No recent trips found.</td>
        </tr>
      `;
      return;
    }

    const latestTrips = [...trips]
      .sort((a, b) => Number(b.id || 0) - Number(a.id || 0))
      .slice(0, 5);

    recentTripsBody.innerHTML = latestTrips
      .map((trip) => {
        const from = trip.pickup_location?.zone || `Location #${trip.pickup_location_id}`;
        const to = trip.dropoff_location?.zone || `Location #${trip.dropoff_location_id}`;
        const vendor = trip.vendor?.name || `Vendor #${trip.vendor_id}`;
        const status = resolveTripStatus(trip);

        return `
          <tr>
            <td>${from}</td>
            <td>${to}</td>
            <td>${vendor}</td>
            <td>${formatAmount(trip.total_amount)}</td>
            <td><span class="status ${statusClass(status)}">${status}</span></td>
          </tr>
        `;
      })
      .join("");
  };

  const renderRecentTripsError = () => {
    if (!recentTripsBody) return;
    recentTripsBody.innerHTML = `
      <tr>
        <td colspan="5">Failed to load recent trips.</td>
      </tr>
    `;
  };

  const init = async () => {
    try {
      const [trips, vendors, payments] = await Promise.all([
        fetchCollection("/trips"),
        fetchCollection("/vendors"),
        fetchCollection("/payments"),
      ]);

      totalTrips.textContent = String(trips.length);
      totalVendors.textContent = String(vendors.length);
      totalPayments.textContent = String(payments.length);
      renderRecentTrips(trips);
    } catch (error) {
      console.error("Failed to load dashboard stats:", error);
      totalTrips.textContent = "-";
      totalVendors.textContent = "-";
      totalPayments.textContent = "-";
      renderRecentTripsError();
    }
  };

  init();
})();
